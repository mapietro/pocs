import os
from pathlib import Path
from typing import List, TypedDict, Union
from langchain_core.messages import HumanMessage, AIMessage, BaseMessage
from langchain_openai import ChatOpenAI
from langgraph.graph import StateGraph, START, END
from dotenv import load_dotenv

load_dotenv()

# ---------- Estado ----------
class AgentState(TypedDict):
    messages: List[BaseMessage]  # pode trocar por Union[HumanMessage, AIMessage] se preferir

# ---------- LLM ----------
llm = ChatOpenAI(model="gpt-4o")

# ---------- Util: carregar histórico do arquivo ----------
def load_history_from_txt(path: str = "logging.txt") -> List[BaseMessage]:
    p = Path(path)
    if not p.exists():
        return []
    msgs: List[BaseMessage] = []
    with p.open("r", encoding="utf-8") as f:
        for raw in f:
            line = raw.strip()
            if not line or line.startswith("Your Conversation Log") or line.startswith("End of Conversation"):
                continue
            if line.startswith("You:"):
                msgs.append(HumanMessage(content=line[4:].strip()))
            elif line.startswith("AI:"):
                msgs.append(AIMessage(content=line[3:].strip()))
            else:
                msgs.append(HumanMessage(content=line))
    return msgs

# ---------- Persistência ----------
def save_log(messages: List[BaseMessage], path: str = "logging.txt") -> None:
    # Garante criação do arquivo mesmo se vazio
    with open(path, "w", encoding="utf-8") as file:
        file.write("Your Conversation Log:\n")
        for m in messages:
            if isinstance(m, HumanMessage):
                file.write(f"You: {m.content}\n")
            elif isinstance(m, AIMessage):
                file.write(f"AI: {m.content}\n")
        file.write("End of Conversation")
    print(f"\nConversation saved to {path}")

# ---------- Nó: process ----------
def process(state: AgentState) -> AgentState:
    """
    Só chama o LLM se a última mensagem for do humano.
    Isso evita erro quando o grafo roda com lista vazia ou estado 'não conversável'.
    """
    msgs = state["messages"]
    if not msgs or not isinstance(msgs[-1], HumanMessage):
        # Não há o que responder; retorna estado como está (sem mutar)
        return {"messages": msgs}

    response = llm.invoke(msgs)
    new_messages = msgs + [AIMessage(content=response.content)]
    print(f"\nAI: {response.content}")
    return {"messages": new_messages}

# ---------- Grafo ----------
graph = StateGraph(AgentState)
graph.add_node("process", process)
graph.add_edge(START, "process")
graph.add_edge("process", END)
agent = graph.compile()

# ---------- Main ----------
def run_chat(): 
    # 1) Carrega histórico existente (se houver) e usa como base do contexto
    conversation_history: List[BaseMessage] = load_history_from_txt("logging.txt")

    try:
        while True:
            user_input = input("Digite sua pergunta (ou 'exit'): ").strip()
            if user_input.lower() == "exit":
                break

            # 2) Adiciona a fala atual do usuário ao histórico em memória
            conversation_history.append(HumanMessage(content=user_input))

            # 3) Invoca o grafo com TODO o histórico (humano + AI)
            result = agent.invoke({"messages": conversation_history})

            # 4) Atualiza o histórico em memória com a resposta do grafo
            conversation_history = result["messages"]

    except KeyboardInterrupt:
        print("\nEncerrado pelo usuário.")

    finally:
        # 5) SEM chamar o LLM aqui. Apenas salva o que já está em memória.
        try:
            save_log(conversation_history, "logging.txt")
        except Exception as e:
            # Última linha de defesa: pelo menos mostre o erro e o caminho
            print(f"Falha ao salvar o log: {e}")
            print(f"Tentando criar um arquivo mínimo...")
            try:
                with open("logging.txt", "w", encoding="utf-8") as f:
                    f.write("Your Conversation Log:\nEnd of Conversation")
                print("Arquivo mínimo 'logging.txt' criado.")
            except Exception as e2:
                print(f"Também falhou ao criar arquivo mínimo: {e2}")

if __name__ == "__main__":
    run_chat()