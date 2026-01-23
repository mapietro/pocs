# uma lista representa uma sequencia de valores

#sintaxe: nome_lista = [valores]

# notas = [5,7,8,6,9]
# print(notas)

# n1 = [4,6,7,8,0,3]
# n2 = [1,6,3,0,12,4]
# valores = n1 + n2

# #==================================================
# #metóds para mamipular a lista

# valores.append(13)
# print(valores)
# valores.pop() # remove o ultimo elemento da lista
# print(valores)

# valores.pop(3) # remove um elemento especifico
# print(valores)

# valores.insert(3,21) # insere na posição 3 o item 21
# print(valores)

# print(12 in valores) #pergunta se um valor esta dentro da lista

#==================================================
# alguns métodos de listas
# print(len(valores))
# print(sorted(valores))

# print(sorted(valores,reverse=True))
# print(sum(valores))

# print(min(valores))
# print(max(valores))

# print(valores)
# print(type(valores))

#==================================================
# acessando um valor da lista
#print(valores[0])

# acessando o ultimo calor
#print(valores[-1])

#mudando um valor
#valores[0]= 9
#print(valores[0])

#==================================================
#Métodos Slice

#imprimindo a partie da posicao X, Y valores
#print(valores[0:2])

#imprimindo todos os itens
#print(valores[0:])

#imprimindo os quatro primeiros itens
#print(valores[:4])

#imprimindo a partir da posição 2 até a posição 5
# (a posição inicial não conta)
#print(valores[2:5])

#imprimir os dois últimos itens
#print(valores[-2:])

# planetas = list() # cria uma lista vazia

planetas = ['Mercúio','Vênus','Marte','Saturno','Urano','Netuno']
for planeta in planetas:
    print(planeta)