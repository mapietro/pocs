from typing import TypedDict
from langgraph.graph import StateGraph, START, END

class AgentState(TypedDict):
    number1: int
    operation: str
    number2: int
    number3: int
    operation2: str
    number4: int
    finalNumber: int
    finalNumber2: int

# --- nós de cálculo (1ª operação) ---
def adder(state: AgentState) -> AgentState:
    """Soma number1 + number2"""
    state["finalNumber"] = state["number1"] + state["number2"]
    return state

def subtractor(state: AgentState) -> AgentState:
    """Subtrai number1 - number2"""
    state["finalNumber"] = state["number1"] - state["number2"]
    return state

# --- nós de cálculo (2ª operação) ---
def adder2(state: AgentState) -> AgentState:
    """Soma number3 + number4"""
    state["finalNumber2"] = state["number3"] + state["number4"]
    return state

def subtractor2(state: AgentState) -> AgentState:
    """Subtrai number3 - number4"""
    state["finalNumber2"] = state["number3"] - state["number4"]
    return state

# --- decisores (routers) ---
def decide_next_node(state: AgentState) -> str:
    """Decide add/sub para a 1ª operação"""
    if state["operation"] == "+":
        return "addition_operation"
    if state["operation"] == "-":
        return "subtraction_operation"
    raise ValueError("operation deve ser '+' ou '-'")

def decide_next_node2(state: AgentState) -> str:
    """Decide add/sub para a 2ª operação"""
    if state["operation2"] == "+":
        return "addition_operation2"
    if state["operation2"] == "-":
        return "subtraction_operation2"
    raise ValueError("operation2 deve ser '+' ou '-'")

# --- grafo ---
graph = StateGraph(AgentState)

# nós de trabalho
graph.add_node("add_node", adder)
graph.add_node("subtract_node", subtractor)
graph.add_node("add_node2", adder2)
graph.add_node("subtract_node2", subtractor2)

# routers (pass-through)
graph.add_node("router", lambda s: s)
graph.add_node("router2", lambda s: s)

# START -> router
graph.add_edge(START, "router")

# router -> (add_node | subtract_node)
graph.add_conditional_edges(
    "router",
    decide_next_node,
    {
        "addition_operation": "add_node",
        "subtraction_operation": "subtract_node",
    },
)

# (add_node | subtract_node) -> router2 // Isso signifca, depois de rodar o add node ou o subtract node, va para router2
graph.add_edge("add_node", "router2")
graph.add_edge("subtract_node", "router2")

# router2 -> (add_node2 | subtract_node2)
graph.add_conditional_edges(
    "router2",
    decide_next_node2,
    {
        "addition_operation2": "add_node2",
        "subtraction_operation2": "subtract_node2",
    },
)

# (add_node2 | subtract_node2) -> END
graph.add_edge("add_node2", END)
graph.add_edge("subtract_node2", END)

app = graph.compile()

# Exemplo do slide:
# number1=10, operation="-", number2=5
# number3=7,  operation2="+", number4=2
state_in = {
    "number1": 10, "operation": "-", "number2": 5,
    "number3": 7,  "operation2": "+", "number4": 2,
    "finalNumber": 0, "finalNumber2": 0
}
result = app.invoke(state_in)
print("finalNumber    =", result["finalNumber"])   # 10 - 5 = 5
print("finalNumber2   =", result["finalNumber2"])  # 7 + 2  = 9


# from IPython.display import Image, display
# display(Image(app.get_graph().draw_mermaid_png()))
