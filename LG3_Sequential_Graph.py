from typing import Dict, TypedDict
from langgraph.graph import StateGraph

class AgentState(TypedDict):
    name: str
    age: str
    skills: list
    final: str

def first_node(state:AgentState) -> AgentState:
    """Primeiro node da sequencia"""

    state['final'] = f'{state['name']}, welcome to the system! '
    return state

def second_node(state:AgentState) -> AgentState:
    """Segundo node da sequencia"""

    state['final'] += f' You are {state['age']} years old! '
    return state

def third_node(state:AgentState) -> AgentState:
    """terceiro node da sequencia"""

    skills = ", ".join(state["skills"])
    state["final"] += f"You have skill in: {skills}"
    return state

graph = StateGraph(AgentState)
graph.add_node("first_node",first_node)
graph.add_node("second_node", second_node)
graph.add_node("third_node", third_node)

graph.set_entry_point('first_node')
graph.add_edge("first_node","second_node")
graph.add_edge("second_node","third_node")
graph.set_finish_point("third_node")

app = graph.compile()
result = app.invoke({"name": "Linda", "age": 221, "skills": ["Python", "Machine Learning", "LangGraph"]})
print(result)


