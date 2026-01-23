# ========================Trocar valores entre duas váriaveis

# var1 = 12
# var2 = 31

# var2, var1 = var1, var2 # troca os valores entre elas
# print(f'Var1 {var1}, var2{var2}')

# ======================== Operador condicional ternário
# var1 = 12
# var2 = 31

# # descobrir qual valor é o menor entre as duas variáveis
# # Operador condicional ternárcio
# # vai retornar o conte[udo de var1, se for menor que var2, se não retorna var2
# menor = var1 if var1 < var2 else var2 
# print(f'Menor valor {menor}')

# # a idéia aqui é, retorne var2 se [var1 < var2] for falso, ou
# # retorne var1 se [var1 < var2] for verdadeiro
# # funciona dentro do print. Bem maluco
# print(f'Menor valor: {(var2, var1)[var1 < var2]}') 

# Generators ========================================
# retorna um tipo de objeto especial do tipo Genarator... 
# Diferente das listas, não joga tudo na memória. Pode ser mais interssante para muitos dados

# valores = [1,2,3,5,7,9,11,13,15]
# # quadrados = [num**2 for num in valores] # usando compreensão de lista
# # print(quadrados)

# # usando genarator
# quadrados = (num**2 for num in valores)   # muito pareceido com comprensão de listas
#                                             # mas são gerados na memória conforme forem solicitados
#                                             # poupando recursos do sistema
# print(quadrados)

# for valor in quadrados:
#     print(valor)

# Função Enumerate ========================================
# iterar em uma lista qualquer, e retornar seus valores e seus indices.

# bebidas = ['Café','Chá','Aguá', 'Suco', 'Refrigerante']

# for i, item in enumerate(bebidas):
#     print(f'Indice: {i}, Item {item}')

# temperaturas = [-1, 10, 5 , -3, 8, 4, -2, -5, 7]

# total = 0

# # Cada indice poderia ser uma cidade.
# for i, t in enumerate(temperaturas):
#     if t < 0:
#         print(f'A temperatura em {i} é negativas, com {t}ºC')

# ate porque a melhor forma de saber o toral de temprraturas negativas seria usando filter
# num_par = list(filter(lambda x: x<1, temperaturas))

#========================================== Gerencimanet de contexto com with

try:
    a = open('frutas.txt', 'r', encoding='utf-8')
    print(a.read())
except IOError:
    print(f'Não foi possível abrie o arquivo')
else:
    a.close()

# usando a forma alternativa com with

with open('frutas.txt', 'r', encoding='utf-8') as a:
    for linha in a:
        print(linha, end ='')




