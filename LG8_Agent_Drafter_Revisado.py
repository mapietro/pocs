from typing import Annotated, Sequence, TypedDict
from dotenv import load_dotenv
from langchain_core.messages import BaseMessage, HumanMessage, AIMessage, ToolMessage, SystemMessage
from langchain_openai import ChatOpenAI
from langchain_core.tools import tool
from langgraph.graph.message import add_messages
from langgraph.graph import StateGraph, END
from langgraph.prebuilt import ToolNode

load_dotenv()

# ===============================
# Memória simples (global)
# ===============================
document_content = ""  # conteúdo canônico do documento

class AgentState(TypedDict):
    messages: Annotated[Sequence[BaseMessage], add_messages]


# ===============================
# Ferramentas (tools)
# ===============================
@tool
def update(content: str) -> str:
    """Atualiza o documento com o conteúdo COMPLETO fornecido."""
    global document_content
    document_content = content
    return f"✅ Documento atualizado: \n{document_content}"

@tool
def save(filename: str) -> str:
    """Save the current document to a text file and finish the process.
    
    Args:
        filename: Name for the text file.
    """
    global document_content

    if not filename.endswith(".txt"):
        filename = f"{filename}.txt"

    # if not document_content.strip():
    #     return "⚠️ Documento está vazio. Use 'update' com o conteúdo completo antes de salvar."

    try:
        with open(filename, "w", encoding="utf-8") as f:
            f.write(document_content)
        print(f"\n💾 Document has been saved to: {filename}")
        return f"Document has been saved successfully to '{filename}'."
    except Exception as e:
        return f"⚠️ Erro ao salvar documento: {str(e)}"

tools = [update, save]
model = ChatOpenAI(model="gpt-4o").bind_tools(tools)


# ===============================
# Nó do agente (simples)
# ===============================
def our_agent(state: AgentState) -> AgentState:
    """
    1) Pede input do usuário no terminal.
    2) Monta o prompt e chama o modelo.
    3) Retorna user_message + response (o ToolNode executa as tools se houver).
    """
    # 1) Entrada do usuário
    user_input = input("\n👤 Você: ")
    user_message = HumanMessage(content=user_input)

    # 2) Prompt do sistema bem objetivo
    system_prompt = SystemMessage(content=f"""
        Você é um assistente de escrita. Você vai ajudar o usuário atualizar e modificar documentos
                                  
        - Se o usuário quiser atualizar ou modificar o conteúdo use a tool 'update' com o conteúdo completo do conteúdo
        - Se o usuário quiser salvar e encerrar, você precisa usar a tool 'save'
        - Sempre mostre o estado do documento atual após as atualizações
        - Responda em PT-BR se o usuário estiver em PT-BR
        
    O estado do documento atual é:\n{document_content}
    """
    )

    # 3) Chamada ao modelo
    all_messages = [system_prompt] + list(state["messages"]) + [user_message]
    response = model.invoke(all_messages)

    # Logs opcionais
    if hasattr(response, "tool_calls") and response.tool_calls:
        print(f"🔧 Ferramentas chamadas: {[tc.get('name') for tc in response.tool_calls]}")

    print(f"\n🤖 IA: {response.content}")
    return {"messages": list(state["messages"]) + [user_message, response]}


# ===============================
# Decisão de continuidade
# ===============================
def should_continue(state: AgentState) -> str:
    """
    Encerra quando detectar ToolMessage de 'save' com sucesso.
    Caso mensagem de tool contenha alerta de documento vazio, continua.
    """
    for msg in reversed(state["messages"]):
        if isinstance(msg, ToolMessage):
            # Se foi SAVE e não retornou erro de vazio, pode encerrar
            if getattr(msg, "name", None) == "save":                
                return "end"
            else:   
                return "continue"            
    return "continue"


# ===============================
# Grafo e execução
# ===============================
graph = StateGraph(AgentState)
graph.add_node("agent", our_agent)
graph.add_node("tools", ToolNode(tools))
graph.set_entry_point("agent")
graph.add_edge("agent", "tools")
graph.add_conditional_edges("tools", should_continue, {"continue": "agent", "end": END})
app = graph.compile()

def run_document_agent():
    print("\n===== DRAFTER (simples) =====")
    print("Exemplos:\n- Cole o texto que quer editar\n- Diga: salvar como proposta_cliente\n")
    state: AgentState = {"messages": []}

    for step in app.stream(state, stream_mode="values"):
        # Mostra apenas resultados de tools (para não poluir)
        if "messages" in step:
            for m in step["messages"][-3:]:
                if isinstance(m, ToolMessage):
                    print(f"\n🛠️ Tool [{getattr(m, 'name', 'tool')}]: {m.content}")
                    break
    print("\n===== DRAFTER FINALIZADO =====")

if __name__ == "__main__":
    run_document_agent()
