# recursividade

#formula geral para o fatorial:
# fatorial(num) = 1, se num = 0 ou se num = 1 'Caso-Base'
# fatorial(num) = num * fatorial(num - 1), para num > 1 'Caso Recursivo'
# 4! = 4 * fatorial(3) = 4 * 3 * fatorial(2) = 4 * 3 * 2 fatorial(1)
# 4! = 4 * 3 * 2 * 1 = 24

def fatorial(numero):
    if numero == 0 or numero == 1:
        return 1
    else:
        return numero * fatorial(numero - 1)
    

if __name__ == '__main__':
    x = int(input('Digite um número inteiro positivo para calcular seu fatorial: '))
    try:
        res = fatorial(x)
    except RecursionError:
        print('O número fornecido é muito grande ou negativo')
    else:
        print(f'O Fatorial de {x} é {res}')

