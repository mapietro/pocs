from typing import Dict, TypedDict
from langgraph.graph import StateGraph, START, END

class AgentState(TypedDict):
    number1: int
    operation: str
    number2: int
    finalNumber: int

def adder(state:AgentState) -> AgentState:
    """este node soma dois números"""

    state['finalNumber'] = state['number1'] + state['number2']
    return state

def subtractor(state:AgentState) -> AgentState:
    """este node substrai dois números"""

    state['finalNumber'] = state['number1'] - state['number2']
    return state

def decide_next_node(state:AgentState) -> AgentState:
    """este node vai escolher o próximo node do grafo"""

    if state['operation'] == "+":        
        return "addition_operation"
    
    if state['operation'] == "-":        
        return "subtraction_operation"
    
graph = StateGraph(AgentState)
graph.add_node("add_node", adder)
graph.add_node("subtract_node", subtractor)
graph.add_node("router", lambda state:state) # basicamente é uma função Passthrough.

graph.add_edge(START, "router")

graph.add_conditional_edges(
    "router", 
    decide_next_node,

    {
        # Edge: Node
        "addition_operation" : "add_node",
        "subtraction_operation" : "subtract_node"
    }

)

graph.add_edge("add_node", END)
graph.add_edge("subtract_node", END)

app = graph.compile()
result = app.invoke({"number1":20, "number2":10, "operation" :"-"})
print(f'O resultado é: {result["finalNumber"]}')

## Outra forma de invokar o grafo
## initial_state = AgentState(number1=10, operation="-", number2=5)
##print(app.invoke(initial_state))
      

        
    


