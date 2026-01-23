from math import sqrt

class NumeroNegativoError(Exception):
    def __init__(self):
        pass

# if __name__ == '__main__':
#     while True:
#         try:
#             num = int(input('Digite um número positivo: '))
#             if num < 0:
#                 raise ArithmeticError
#         except ArithmeticError:
#             print('Foi fornecido um número negativo')
#         else:
#             print(f'A raiz quadrada de {num} é {sqrt(num)}')
#             print('Fim do Cálculo')
#             break


if __name__ == '__main__':
    while True:
        try:
            num = int(input('Digite um número positivo: '))
            if num < 0:
                raise NumeroNegativoError
        except NumeroNegativoError:
            print('Foi fornecido um número negativo')
        else:
            print(f'A raiz quadrada de {num} é {sqrt(num)}')
            print('Fim do Cálculo')
            break
      
    
