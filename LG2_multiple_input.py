from typing import Dict, TypedDict
from langgraph.graph import StateGraph, START, END
from functools import reduce
import math

class AgentState(TypedDict): #our state schema
    values : list
    operation: str
    name: str
    result :str

def process_values(state: AgentState) -> AgentState:
    """ Método para processar multiplos inputs"""
    
    ## olha essa insanidade, usa reduce e lambda para multiplicar
    #state["result"] = "Olá camarada {}".format(state['name']),'A soma dos valores é {}'.format(sum(state["values"])) if state['operation'] == "+" else 'A multiplicação dos valores é {}'.format(reduce(lambda x,y: x*y,state['values']))

    ## agora, do Jeito normal e legivel, 
    operation = state['operation']
    resultado = 0
    if operation == "+" :
        resultado = sum(state['values'])
        state['result'] = f'Ola Camarada {state['name']}, A some dos valores é {resultado}'
    elif operation == "*":
        resultado = math.prod(state['values'])
        state['result'] = f'Ola Camarada {state['name']}, A multiplicaso dos valores é {resultado}'
    else :
        state['result'] = f'Ola Camarada {state['name']}, não consigo executar essa operação, ou nenhuma foi informada'

    return state


graph = StateGraph(AgentState)

graph.add_node("processor",process_values)
# ## graph.set_entry_point("processor")
# ## graph.set_finish_point("processor")

# """ Essa é a forma mais moderda"""
graph.add_edge(START, "processor")
graph.add_edge("processor", END)

app = graph.compile()

aswers  = app.invoke({"values": [1,2,3,4], "name": "Márcio", "operation": "*"})
print(aswers["result"])