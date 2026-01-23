## compreensão de listas
# sintaxe : [expressão for item in lista]
# onde expressão é a expressão que sera avaliada/executada para cada elemento em "lista"
# e "item" é a variavel que representa cada elemento em lista

# numeros = [1,4,7,9,10,12,21]

# # exemplo retornando o quadrado para casa item
# # da list usando map e lambda, como já aprendemos
# # quadrados = list(map(lambda x: x**2,numeros)) 

# # agora usando compreensão de lista. Bem limpo. Aqui nsó executa uma expressão para cada item da lista
# quadrados = [num**2 for num in numeros]
# print(quadrados)

# criar uma lista de números pares de 0 a 10 ( show, usando range)
# o que ele faz é testar para cada numero de 1 a 10, se é par
# retornando true, é par
# pares = [num for num in range(11) if num % 2 == 0]
# print(pares)

#exemplo com texto
# contar a quantidade de vogais em uma frase. Fazer isso é muipo poderoso. 
# imagina set tivesse que fazer um algoritmo para isso.

# frase = 'A lógica é apenas o princípio da sabedoria, e não o seu fim'
# vogais = ['a','e','i','o','u','á','é','í','ó','u']

# o que ele faz aqui é para cada elemento da lista, testar se esta na lista de vogais
# retornando true, é uma vogal
# lista_de_vogais = [v for v in frase if v in vogais]
# print(f'A frase possui {len(lista_de_vogais)} vogais')
# print(lista_de_vogais)

# distributiva entre valores de duas listas, usando dois laços for
# se as listas fossem muito grandes, passaria elas como parametro, 
# mas para o exmplo, são pequenas,e foram criadas dentro do contexto dos parametros
# ele vai fazer 2*10, 2*20, 2*30... depois 3*10, 3*20, 3*30... depois 5*10,5*20,5*30
#distributiva = [k * m for k in[2,3,5] for m in [10,20,30]]
#print(distributiva)

query = "crie"
RAG_KNOWLEDGE = [
    "Faça perguntas abertas",
    "Crie opções para lidar com clientes agressivos",
    "Evite começar pelo preço"
]

pares = [num  for num in range(11) if num % 2 == 0]
print(pares)

def rag_louca(query):
    return [doc for doc in RAG_KNOWLEDGE if any(word in doc.lower() for word in query.split())]


def simple_rag(query):
    palavras = query.lower().split()
    resultados = []

    for doc in RAG_KNOWLEDGE:
        texto = doc.lower()

        # verifica se ALGUMA palavra da busca aparece no documento
        for palavra in palavras:
            if palavra in texto:
                resultados.append(doc)
                break  # já achou uma palavra, não precisa testar as outras

    return resultados[:2]

# print(simple_rag(query))
print(rag_louca(query))



