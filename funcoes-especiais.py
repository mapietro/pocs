# funções lambda ou anônimas
# sintaxe de uma função lambda:
# lambda argumentos: expressão

# quadrado = lambda x:x**2

# for i in range(1,11):
#     print(quadrado(i))


# par = lambda x:  x%2 == 0
# print(par(9))

# f_c = lambda f: (f - 32) * 5/9
# print(f_c(32))
#======================================================

# função map() é uma função de ordem superior, que pode receber outras funcões como argumento
# ou retornar outras funções como resultado
# sintaxe:::
# map(função: iteravel)

# num =[1,2,3,4,5,6,7,8]
# dobro = list(map(lambda x:x*2, num))
# print(dobro)

# palavras = ['Python', 'é', 'uma', 'linguagem', 'de', 'programação']
# maiusculas = list(map(str.upper, palavras))
# print(maiusculas)

# def dobro(x):
#     return x*2

# num =[1,2,3,4,5,6,7,8]
# # O map, intera em casa elemento da lista, passando cada elemento pra função. 
# aqui um exmeplo sem lambda, chamando uma função criada por mim
# num_dobro = list(map(dobro,num))
# print(num_dobro)

#======================================================

# função filter
# filter(função, sequencia)

# def numeros_pares(n):
#     return n % 2 == 0

# numeros = [1,2,3,4,5,6,7,8,9,10,11,12,13]
# # a questão do filter é receber um booleano, sempre que for verdadeiro, manda pra lista o valor que retornou verdadeiro
# num_par = list(filter(numeros_pares, numeros))
# print(num_par)

# # usando com lambda
# num_impar = list(filter(lambda x: x%2 != 0,numeros))
# print(num_impar)

#======================================================

# função reduce(), faz operaçao cumulativa
# sintaxe: reduce(função, sequencia, valor_inicial)

#from functools import reduce

# def mult(x,y):
#     return x * y

# numeros = [1,2,3,4,5,6]

# # veja que interessante, foi feito um fatorial, cada valor retornado foi usado como
# # parametro para a próxima chamada a função. Esse é o objetivo do reduce.
# total = reduce(mult,numeros)
# print(total)

# soma cumulativa dos quadrados de valores usando expressão lambda
# objetivo é fazer isso ((1² + 2²))² + 3²)² + 4²

# from functools import reduce

# numeros = [1,2,3,4]

# total = reduce(lambda x,y: x**2 + y**2, numeros)
# print(total)

# def numeros_pares(n):
#      return n % 2 == 0

temperaturas = [-1, 10, 5 , -3, 8, 4, -2, -5, 7]# a questão do filter é receber um booleano, sempre que for verdadeiro, manda pra lista o valor que retornou verdadeiro
num_par = list(filter(lambda x: x<1, temperaturas))
print(f'Há {len(num_par)} temperaturas negativa')

