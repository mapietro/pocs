import os
from typing import List, TypedDict, Union
from langchain_core.messages import HumanMessage, AIMessage
from langchain_openai import ChatOpenAI
from langgraph.graph import StateGraph, START, END
from dotenv import load_dotenv # Para guardar chave AI ou configugações

load_dotenv()


""" Agente , Estado"""
class AgentState(TypedDict) :
    messages: List[Union[HumanMessage, AIMessage]] # Aceita os dois tipos. j

llm = ChatOpenAI(model="gpt-4o")
   

def process(state: AgentState) -> AgentState:
    """ Este Node vai salvar o input que o usuário fornecer"""
    response = llm.invoke(state['messages'])

    state['messages'].append(AIMessage(content=response.content))
    print(f'\nAI: {response.content}')
    print(f"CURRENT STATE: {state['messages']}")

    return state

graph = StateGraph(AgentState)
graph.add_node("process",process)
graph.add_edge(START, "process")
graph.add_edge("process", END)
agent = graph.compile()

conversation_history = []

user_input = input('Digite sua pergunta: ')
while user_input != "exit":
    conversation_history.append(HumanMessage(content=user_input))

    # invoke com todo o histórico da conversa(toda conversa é enviada)
    result = agent.invoke({'messages' : conversation_history}) 

    print(result['messages'])
    conversation_history = result['messages']
    
    user_input = input('Digite sua pergunta: ')


with open("logging2.txt", "w", encoding='utf-8') as file:
    file.write("Your Conversation Log:\n")

    for message in conversation_history:
        if isinstance(message, HumanMessage):
            file.write(f"You: {message.content}\n")
        elif isinstance(message, AIMessage) :
            file.write(f"AI: {message.content}\n\n")
    file.write("End of Conversation")

print("Conversation saved to logging.txt")