from typing import Dict, TypedDict
from langgraph.graph import StateGraph, START, END

class AgentState(TypedDict): #our state schema
    message : str


def greeting_node(state: AgentState) -> AgentState:
    """ Node simples que adiciona uma mensagem de saudação ao state"""
    state['message'] = 'hey ' + state['message'] + ', How is your day going'

    return state

graph = StateGraph(AgentState)

graph.add_node("greeter",greeting_node)
## graph.set_entry_point("greeter")
## graph.set_finish_point("greeter")

""" Essa é a forma mais moderda"""
graph.add_edge(START, "greeter")
graph.add_edge("greeter", END)

app = graph.compile()

result  = app.invoke({"message": "Bob"})
print(result["message"])
    