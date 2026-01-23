"""
RAG com LangGraph + LangChain + Chroma (com melhorias práticas)
- Leitura de PDF → chunking → indexação vetorial (Chroma) → retriever (MMR) → tool-calls → LLM
- Comentários em PT-BR e marcações de MELHORIA para te guiar no que foi ajustado/otimizado.

Pré-requisitos de instalação (em um venv de preferência):
  pip install langgraph langchain langchain-openai langchain-community langchain-text-splitters langchain-chroma python-dotenv chromadb pypdf

Estrutura geral:
  1) Carregar variáveis de ambiente (.env)
  2) Instanciar LLM + embeddings
  3) Carregar PDF e fazer split em chunks
  4) Criar/Abrir Chroma com persistência (evitando reindexação duplicada)  [MELHORIA]
  5) Criar retriever com MMR para diversidade                           [MELHORIA]
  6) Definir tool do retriever, incluindo metadados (página) para citação [MELHORIA]
  7) Montar grafo LangGraph: llm → (condicional) → retriever_agent → llm → ...
  8) Loop CLI (com opcional de manter histórico entre turns)             [MELHORIA]
"""

from dotenv import load_dotenv
import os
from typing import TypedDict, Annotated, Sequence, List

# LangGraph (orquestração)
from langgraph.graph import StateGraph, END

# Tipos de mensagens (LangChain Core)
from langchain_core.messages import BaseMessage, SystemMessage, HumanMessage, ToolMessage

# Para "somar" listas de mensagens no estado
from operator import add as add_messages

# OpenAI (LLM + Embeddings)
from langchain_openai import ChatOpenAI, OpenAIEmbeddings

# Ingestão e chunking
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter

# VectorStore
from langchain_chroma import Chroma

# Tools (para expor o retriever ao LLM via tool-calls)
from langchain_core.tools import tool


# ---------------------------------------------------------------------
# 1) Carregar variáveis de ambiente (.env)
# ---------------------------------------------------------------------
load_dotenv()
assert os.getenv("OPENAI_API_KEY"), "OPENAI_API_KEY não encontrada no ambiente (.env)."


# ---------------------------------------------------------------------
# 2) Modelos (LLM + Embeddings)
# ---------------------------------------------------------------------
# temperature=0 deixa as respostas mais determinísticas (bom para RAG, reduz alucinação)
llm = ChatOpenAI(model="gpt-4o", temperature=0)

# Modelo de embeddings (coerência entre indexação e consulta é o mais importante)
embeddings = OpenAIEmbeddings(model="text-embedding-3-small")


# ---------------------------------------------------------------------
# 3) Carregar PDF e fazer chunking
# ---------------------------------------------------------------------
pdf_path = "Stock_Market_Performance_2024.pdf"  # coloque seu arquivo na mesma pasta ou use caminho absoluto

if not os.path.exists(pdf_path):
    raise FileNotFoundError(f"PDF file not found: {pdf_path}")

pdf_loader = PyPDFLoader(pdf_path)

try:
    # 'pages' é uma lista de Document (cada página vira um doc)
    pages = pdf_loader.load()
    print(f"PDF carregado com sucesso: {len(pages)} páginas")
except Exception as e:
    print(f"Erro ao carregar PDF: {e}")
    raise

# Split recursivo cuida de limites lógicos; overlap ajuda a manter contexto entre chunks adjacentes
text_splitter = RecursiveCharacterTextSplitter(
    chunk_size=1000,
    chunk_overlap=200
)

pages_split = text_splitter.split_documents(pages)
print(f"Total de chunks gerados: {len(pages_split)}")


# ---------------------------------------------------------------------
# 4) VectorStore (Chroma) com persistência
#    MELHORIA: evitar reindexar em execuções repetidas (duplicação de vetores)
# ---------------------------------------------------------------------
# OBS: em Windows o caminho abaixo funciona; se preferir, troque por Path(...).
persist_directory = r".\chroma_rag_demo"   # ajuste à vontade
collection_name = "stock_market"

# Garante que a pasta existe
os.makedirs(persist_directory, exist_ok=True)

# Abre a coleção (se não existir, será criada)
vectorstore = Chroma(
    embedding_function=embeddings,
    persist_directory=persist_directory,
    collection_name=collection_name,
)

# MELHORIA: só indexa se estiver vazia (evita duplicar vetores em reexecução)
try:
    current_count = vectorstore._collection.count()  # atributo "interno" do Chroma; prático para checar
except Exception:
    current_count = 0

if current_count == 0:
    vectorstore.add_documents(pages_split)
    print("Indexação feita no Chroma (coleção estava vazia).")
else:
    print(f"Usando coleção existente no Chroma (itens atuais: {current_count}).")


# ---------------------------------------------------------------------
# 5) Retriever
#    MELHORIA: usar MMR para diversidade de trechos (reduz redundância e melhora cobertura)
# ---------------------------------------------------------------------
# Opção A (recomendada): MMR
retriever = vectorstore.as_retriever(
    search_type="mmr",
    search_kwargs={"k": 6, "fetch_k": 20, "lambda_mult": 0.2}  # ajuste fino de diversidade
)

# Opção B (clássica): Similarity pura
# retriever = vectorstore.as_retriever(
#     search_type="similarity",
#     search_kwargs={"k": 5}
# )


# ---------------------------------------------------------------------
# 6) Tool do retriever
#    MELHORIA: retornar também a página para permitir citação precisa no output do LLM
# ---------------------------------------------------------------------
@tool
def retriever_tool(query: str) -> str:
    """
    Busca trechos relevantes do PDF 'Stock Market Performance 2024' e
    devolve excertos com metadados (página) para facilitar citações.
    """
    docs = retriever.invoke(query)

    if not docs:
        return "No relevant information found in the document."

    results: List[str] = []
    for i, doc in enumerate(docs, start=1):
        page = doc.metadata.get("page", "?")  # PyPDFLoader costuma preencher "page"
        # MELHORIA (token-conscious): se quiser economizar tokens, pode resumir cada chunk aqui.
        # Ex.: limitar tamanho do doc.page_content ou aplicar um "mini-sumário" com outro LLM.
        results.append(f"[Doc {i} | page {page}]\n{doc.page_content}")

    return "\n\n".join(results)


# Vincula a tool ao LLM para que ele possa chamar via tool-calls nativos
tools = [retriever_tool]
llm = llm.bind_tools(tools)


# ---------------------------------------------------------------------
# 7) Estado do agente + nós do grafo (LangGraph)
# ---------------------------------------------------------------------
class AgentState(TypedDict):
    # 'messages' acumula o histórico (System, Human, AI e Tool)
    messages: Annotated[Sequence[BaseMessage], add_messages]


def should_continue(state: AgentState) -> bool:
    """
    Verifica se a última mensagem do LLM contém tool-calls.
    Se sim, seguimos para o nó executor de ferramentas; se não, finalizamos.
    """
    ai_msg = state["messages"][-1]
    return hasattr(ai_msg, "tool_calls") and len(ai_msg.tool_calls) > 0


# Prompt de sistema (instruções do papel do agente)
system_prompt = (
    "You are an intelligent AI assistant who answers questions about Stock Market "
    "Performance in 2024 based on the PDF loaded into your knowledge base. "
    "Use the retriever tool to find information. You may call tools multiple times. "
    "If needed, look up information first, then ask follow-ups. "
    "Always cite the specific passages (with page numbers) used in your answers."
)

# Dicionário de tools por nome (para despacho no nó executor)
tools_dict = {t.name: t for t in tools}


def call_llm(state: AgentState) -> AgentState:
    """
    Nó do LLM:
    - Prepara o contexto (System + histórico) e chama o modelo.
    - O retorno pode conter tool-calls (o LangGraph checa com 'should_continue').
    """
    messages = [SystemMessage(content=system_prompt)] + list(state["messages"])
    ai = llm.invoke(messages)  # pode vir com tool_calls
    return {"messages": [ai]}


def take_action(state: AgentState) -> AgentState:
    """
    Nó executor de ferramentas:
    - Lê as tool-calls emitidas pela última AIMessage.
    - Executa cada tool e devolve ToolMessage (com tool_call_id correspondente).
    - O próximo passo volta ao LLM para ele "usar" os resultados das tools.
    """
    tool_calls = state["messages"][-1].tool_calls
    results: List[ToolMessage] = []

    for tc in tool_calls:
        name = tc["name"]
        args = tc.get("args", {})
        query = args.get("query", "")
        print(f"[Tool] Chamando: {name} | query={query!r}")

        if name not in tools_dict:
            result = "Incorrect tool name. Please retry using an available tool."
        else:
            # Chamada síncrona da tool
            result = tools_dict[name].invoke(query)
            print(f"[Tool] Tamanho do resultado: {len(str(result))}")

        # Envia a resposta da tool de volta ao LLM (ToolMessage precisa do id da chamada)
        results.append(ToolMessage(tool_call_id=tc["id"], name=name, content=str(result)))

    print("[Tool] Execução das tools concluída. Voltando ao modelo…")
    return {"messages": results}


# Montagem do grafo
graph = StateGraph(AgentState)
graph.add_node("llm", call_llm)
graph.add_node("retriever_agent", take_action)

# Fluxo: llm → (se pediu tool) retriever_agent → llm → ... → END
graph.add_conditional_edges("llm", should_continue, {True: "retriever_agent", False: END})
graph.add_edge("retriever_agent", "llm")
graph.set_entry_point("llm")

# Compila o grafo em um "runnable"
rag_agent = graph.compile()


# ---------------------------------------------------------------------
# 8) Loop interativo (CLI)
#    MELHORIA: opção de manter histórico entre perguntas (multi-turn real)
# ---------------------------------------------------------------------
USE_HISTORY = True  # mude para False se quiser cada pergunta "isolada"

def running_agent():
    print("\n=== RAG AGENT ===")
    history: List[BaseMessage] = []

    while True:
        user_input = input("\nWhat is your question: ")
        if user_input.lower() in ["exit", "quit"]:
            print("Até mais!")
            break

        # Se for conversa contínua, reaproveita histórico; caso contrário, zera a cada turn
        if USE_HISTORY:
            history.append(HumanMessage(content=user_input))
            state_in = {"messages": history}
        else:
            state_in = {"messages": [HumanMessage(content=user_input)]}

        # Executa o grafo
        result = rag_agent.invoke(state_in)

        # A última mensagem é a AIMessage final (ou a mais recente, caso ainda haja tools)
        final_msg = result["messages"][-1]
        print("\n=== ANSWER ===")
        print(final_msg.content)

        # Atualiza histórico apenas no modo multi-turn
        if USE_HISTORY:
            history.extend(result["messages"])  # adiciona a AIMessage (e eventualmente ToolMessages)

if __name__ == "__main__":
    running_agent()


# ---------------------------------------------------------------------
# 9) Ideias de MELHORIA futuras (opcionais)
# ---------------------------------------------------------------------
# - Reranking: após o retriever, aplicar um reranker dedicado para ordenar melhor os trechos.
# - Limitar tokens na Tool: resumir cada chunk (ou truncar) antes de devolver ao LLM,
#   reduzindo custo/latência e evitando estourar contexto.
# - Formato de citação padronizado: “(p. 12)”, ou “Fonte: PDF, p. 12”.
# - Avaliação: crie um pequeno "harness" de perguntas/ground-truth para medir precisão e custo.
# - Multi-arquivos: carregar vários PDFs e incluir no metadata o “source” (nome do arquivo),
#   permitindo citações do tipo “Relatório X (p. 7)”.
