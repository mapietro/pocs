# def soma(a,b):
#     return a+b # posso ou não retornar, a função pode executar algo sem retorno

# total = soma(5,4)
# print(f'O resuttado da soma é {total}')

# def div(k,j):
#     if j!= 0:
#         return k/j
#     else :
#         return 'Impossível dividir por zero!'

# if __name__ == "__main__":
#     a = int(input('Digite um número'))
#     b = int(input('Digite outro número'))

#     r = div(a,b)
#     print(f'{a} dividido por {b} é igual a {r}')

# def quadrado(val):
#     quadrados = []
#     for x in val:
#         quadrados.append(x ** 2)
#     return quadrados

# if __name__ == "__main__":
#     valores = [2,5,7,9,12]
#     resultados = quadrado(valores)

#     for g in resultados:
#         print(g)


# #def contar(num=11, caractere='+'):
# def contar(caractere, num=11):  # na construção das funçoes, primeiro informamos
#     for i in range(1, num):     # os parametros obrigatõrios, e depois os opcionais
#         print(caractere)        # pois os opcionais já tem um valor default


# if __name__ == "__main__":
#     # contar()
#     # contar(caractere='&')   # como o parametro recebido pela função rem um nome
#                             # e é inicializado, precisa usar obrigatoriamente
#                             # o mesmo nome ao passar um novo parametro
#     # contar(num=3, caractere='*') 

#     # contar(6)   # se passar os parametros na ordem correta, seus nomes
#                 # não precisam ser informador. só preciso informar
#                 # se forem passados fora de ordem    

#     contar('@')

x = 5
y = 6
z = 3

def soma_mult(a,b ,c=0):
    if c==0:
        return a * b
    else:
        return a + b +c
    
if __name__ == '__main__':
    res = soma_mult(x,y, z)
    print(res)