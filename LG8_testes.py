from typing import Annotated, Sequence, TypedDict
from dotenv import load_dotenv
from langchain_core.messages import (
    BaseMessage,
    HumanMessage,
    AIMessage,
    ToolMessage,
    SystemMessage,
)
from langchain_openai import ChatOpenAI
from langchain_core.tools import tool
from langgraph.graph.message import add_messages
from langgraph.graph import StateGraph, START, END
from langgraph.prebuilt import ToolNode
import json

load_dotenv()

# ===============================
# Estado simples (global)
# ===============================
document_content = ""  # conteúdo canônico do documento (para tools)

class AgentState(TypedDict):
    messages: Annotated[Sequence[BaseMessage], add_messages]


# ===============================
# Ferramentas (tools)
# ===============================
@tool
def update(content: str) -> str:
    """
    Atualiza o documento com o CONTEÚDO COMPLETO final após a edição.
    Retorna JSON: {"ok": true, "content": "<novo_conteudo>"}
    """
    global document_content
    document_content = content
    return f"Document has been updated successfully! The current content is:\n{document_content}"

@tool
def save(filename: str) -> str:
    """
    Salva o documento atual em um arquivo .txt.
    - Se o documento estiver vazio, NÃO salva e retorna ok=false.
    Retorna JSON:
      - sucesso: {"ok": true, "filename": "<nome>.txt", "bytes": <tamanho>}
      - erro:    {"ok": false, "error": "..."}
    """
    global document_content

    # if not document_content.strip():
    #     return json.dumps(
    #         {"ok": False, "error": "Documento vazio. Use 'update' com o conteúdo completo antes de salvar."},
    #         ensure_ascii=False,
    #     )

    if not filename.endswith(".txt"):
        filename = f"{filename}.txt"

    try:
        with open(filename, "w", encoding="utf-8") as f:
            f.write(document_content)
        print(f"\n💾 Document has been saved to: {filename}")
        return f"Document has been saved successfully to '{filename}'."
        # return json.dumps({"ok": True, "filename": filename, "bytes": len(document_content)}, ensure_ascii=False)
    except Exception as e:
        return f"Error saving document: {str(e)}"

tools = [update, save]

# Modelo com ferramentas vinculadas
model = ChatOpenAI(model="gpt-4o").bind_tools(tools)


# ===============================
# Nó: agente (LLM)
# ===============================
def our_agent(state: AgentState) -> AgentState:
    """
    Monta o prompt e chama o modelo. O modelo deve agir direto (update/save).
    """
    system_prompt = SystemMessage(
        content=(
            "Você é o Drafter, um assistente de escrita focado em AÇÃO.\n"
            "Regras IMPORTANTES:\n"
            "1) Nada de cumprimentos genéricos. Vá direto ao ponto.\n"
            "2) Se o usuário pediu edição, APLIQUE a edição e CHAME 'update' passando o CONTEÚDO COMPLETO final.\n"
            "3) NUNCA chame 'save' com documento vazio. Só chame 'save' após um 'update' bem-sucedido.\n"
            "4) Suas ferramentas retornam JSON. NÃO reescreva o JSON de volta; apenas deixe o ToolNode lidar com ele.\n"
            "5) Após 'update', mostre o conteúdo atual do documento para conferência.\n"
            "6) Se o usuário escrever em PT-BR, responda em PT-BR.\n\n"
            "Dica: para salvar, o usuário dirá algo como: 'salvar como proposta_cliente'.\n"
        )
    )

    # O histórico já contém a fala do usuário (inserida por get_user_input)
    all_messages = [system_prompt] + list(state["messages"])

    response = model.invoke(all_messages)

    # Log simples de tool calls (nome + args)
    if hasattr(response, "tool_calls") and response.tool_calls:
        calls = []
        for tc in response.tool_calls:
            calls.append({"name": tc.get("name"), "args": tc.get("args")})
        print(f"\n🔧 Tool calls: {json.dumps(calls, ensure_ascii=False)}")

    return {"messages": list(state["messages"]) + [response]}


# ===============================
# Nó: coletar input do usuário
# ===============================
def get_user_input(state: AgentState) -> AgentState:
    user_input = input("\n👤 Você: ")
    user_message = HumanMessage(content=user_input)
    return {"messages": list(state["messages"]) + [user_message]}


# ===============================
# Decisão de continuidade
# ===============================
def _parse_tool_json(s: str):
    try:
        return json.loads(s)
    except Exception:
        return None

def should_continue(state: AgentState) -> str:
    """
    Encerra SOMENTE quando a última tool executada for 'save' E ok=true.
    Caso 'save' retorne ok=false (ex.: documento vazio), continua.
    """
    for message in reversed(state["messages"]):
        if isinstance(message, ToolMessage) and getattr(message, "name", None) == "save":
            data = _parse_tool_json(message.content or "")
            if isinstance(data, dict) and data.get("ok") is True:
                return "end"
            else:
                # save falhou -> continue (o retorno terá o motivo)
                return "continue"
        if isinstance(message, ToolMessage):
            # Outra tool (update) -> continuar
            return "continue"
        if isinstance(message, AIMessage):
            return "continue"
    return "continue"


# ===============================
# Impressão amigável
# ===============================
def print_messages(messages: Sequence[BaseMessage]) -> None:
    if not messages:
        return
    for m in messages[-3:]:
        if isinstance(m, ToolMessage):
            # Tentar decodificar JSON de tools
            data = _parse_tool_json(m.content or "")
            if data:
                print(f"\n🛠️ Tool [{getattr(m, 'name', 'tool')}]: {json.dumps(data, ensure_ascii=False)}")
            else:
                print(f"\n🛠️ Tool [{getattr(m, 'name', 'tool')}]: {m.content}")
        elif isinstance(m, AIMessage) and m.content:
            print(f"\n🤖 IA: {m.content}")


# ===============================
# Grafo
# ===============================
graph = StateGraph(AgentState)

graph.add_node("get_user_input", get_user_input)
graph.add_node("agent", our_agent)
graph.add_node("tools", ToolNode(tools))

graph.add_edge(START, "get_user_input")
graph.add_edge("get_user_input", "agent")
graph.add_edge("agent", "tools")

graph.add_conditional_edges(
    "tools",
    should_continue,
    {
        "continue": "get_user_input",
        "end": END,
    },
)

app = graph.compile()


# ===============================
# Runner
# ===============================
def run_document_agent():
    print("\n===== DRAFTER =====")
    print(
        "Dica: descreva o que quer escrever/editar e cole o texto completo quando for o caso.\n"
        "Para salvar, diga: salvar como <nome_arquivo>\n"
    )

    state: AgentState = {"messages": []}

    for step in app.stream(state, stream_mode="values"):
        if "messages" in step:
            print_messages(step["messages"])

    print("\n===== DRAFTER FINALIZADO =====")

if __name__ == "__main__":
    run_document_agent()
