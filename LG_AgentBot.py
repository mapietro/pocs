from typing import List, TypedDict
from langchain_core.messages import HumanMessage
from langchain_openai import ChatOpenAI
from langgraph.graph import StateGraph, START, END
from dotenv import load_dotenv # Para guardar chave AI ou configugações
import os

load_dotenv()

""" Agente simples, um BOT sem memória. O mais simples possível"""
class AgentState(TypedDict) :
    messages: List[HumanMessage]


llm = ChatOpenAI(model="gpt-4o")


def process(state: AgentState) -> AgentState:
    response = llm.invoke(state['messages'])
    print(f'\nAI: {response.content}')
    return state

graph = StateGraph(AgentState)
graph.add_node("process",process)
graph.add_edge(START, "process")
graph.add_edge("process", END)
agent = graph.compile()

user_input = input('Digite sua pergunta: ')
while user_input != "exit":
    agent.invoke({'messages' : [HumanMessage(content=user_input)]})
    user_input = input('Digite sua pergunta: ')