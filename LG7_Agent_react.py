from typing import Annotated, Sequence, TypedDict
from dotenv import load_dotenv # Para guardar chave AI ou configugações
from langchain_core.messages import BaseMessage
from langchain_core.messages import ToolMessage
from langchain_core.messages import SystemMessage
from langchain_openai import ChatOpenAI
from langchain_core.tools import tool
from langgraph.graph.message import add_messages
from langgraph.graph import StateGraph, START, END
from langgraph.prebuilt import ToolNode


load_dotenv()

"""
O Annotated[..., add_messages] aqui no AgentState define que messages é uma sequência (Sequence[BaseMessage]) e que deve acumular mensagens (não substituir).

Então, cada nó do grafo deve devolver um dicionário com a chave messages,
cujo valor é uma lista de novas mensagens a adicionar ao histórico.

Mesmo que seja só uma mensagem, precisa estar dentro de uma lista. 

Por isso, retornamos agora nos agentes {"messages": [response]} e não mais o state"""
class AgenteState(TypedDict):
    messages: Annotated[Sequence[BaseMessage], add_messages] # Iundica apendar mensagebns


@tool
def add(a: int, b:int):
    """This is an addition function that adds 2 numbers together"""
    return a + b

@tool
def subtract(a: int, b:int):
    """This is an substraction function that substract 2 numbers"""
    return a - b

@tool
def multiply(a: int, b:int):
    """This is a multiply function that multiplies 2 numbers"""
    return a * b

tools = [add,subtract,multiply]

model = ChatOpenAI(model = "gpt-4o").bind_tools(tools)

def model_call(state:AgenteState) -> AgenteState:
    system_prompt = SystemMessage(content = 
        "You are my AI assistant, please answer my query  to the best of yout ability"                                  
    )
    response = model.invoke([system_prompt] + state["messages"])
    return {"messages": [response]}

def should_continue(state:AgenteState) -> AgenteState:
    messages = state['messages']
    last_message = messages[-1]
    if not last_message.tool_calls:
        return "end"
    else:
        # print("toooooolllll calllllssss________________________")        
        # for n in last_message.tool_calls:            
        #     print(n["name"])
        return "continue"
    
    
graph = StateGraph(AgenteState)
graph.add_node("our_agent", model_call)
tool_node = ToolNode(tools=tools)
graph.add_node("tools", tool_node)
graph.set_entry_point("our_agent")
graph.add_conditional_edges(
    "our_agent",
    should_continue,
    {
        "continue": "tools",
        "end" : END,
    },
)
graph.add_edge("tools", "our_agent")

app = graph.compile()

def print_stream(stream):
    for s in stream:
        message = s["messages"][-1] # Pega a ultima mensagem da lista de mensagens, Em outras palavras: a mensagem nova gerada naquela iteração.        
        """ 
            Essa verificação é uma salvaguarda para o primeiro estado (ou casos raros) em que o LangGraph ainda não converteu as mensagens em objetos BaseMessage.
            Ela evita erro de atributo (AttributeError: 'tuple' object has no attribute 'pretty_print') e garante que o código funcione do início ao fim.
            Se for uma tupla → imprime simples, tipo ('user', 'Add 3 + 4')

            Se for um objeto LangChain (BaseMessage) → usa o método pretty_print(),
            que formata de forma bonitinha (ex: “🧠 AI: O resultado é 7.”).        
        """
        if isinstance(message, tuple):
            print("Uma tupla??? ")
            print(message)        
        else:                    
            message.pretty_print()            

#inputs = {"messages" : [("user", "Add 40 + 12 and then multiply the result by 6 and the final result, substract 5")]}
inputs = {"messages" : [("user", "Add 40 + 12")]}
# result = app.invoke(inputs)
# for n in result["messages"]:
# # #     #print(type(result["messages"]))
# # #     print("tipo\n")
# # #     print(type(n))
# # #     #print("o que tem ai?\n")
# # #     #print(n)
#       print(n.pretty_print())

"""How the stream method should emit outputs.

- `"values"`: Emit all values in the state after each step, including interrupts.
    When used with functional API, values are emitted once at the end of the workflow.
- `"updates"`: Emit only the node or task names and updates returned by the nodes or tasks after each step.
    If multiple updates are made in the same step (e.g. multiple nodes are run) then those updates are emitted separately.
- `"custom"`: Emit custom data using from inside nodes or tasks using `StreamWriter`.
- `"messages"`: Emit LLM messages token-by-token together with metadata for any LLM invocations inside nodes or tasks.
- `"checkpoints"`: Emit an event when a checkpoint is created, in the same format as returned by `get_state()`.
- `"tasks"`: Emit events when tasks start and finish, including their results and errors.
- `"debug"`: Emit `"checkpoints"` and `"tasks"` events for debugging purposes.
"""

print_stream(app.stream(inputs, stream_mode="values"))















