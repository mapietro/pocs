# tratamento de exceções; um objeto que representa um erro que ocorreu ao 
# executar o programa
# usar blocos try... except 
# tipos de exceção comuns já fornecidas pelo python::
# Exception, ArithmeticError, OverflowError, ImportError, ZeroDivisionError
# NameError, IOError, IndentationError, RecursionError, TypeError


def div(k,j):
    return round(k / j,2)

if __name__ == '__main__':
    while True:
        try:        
            n1 = int(input('Digite um número: '))
            n2 = int(input('Digite outro número: '))
            break
        except ValueError:
            print('Ocorreu um erro ao ler o valor, tente novamente.')
            # laço while prosegue enquanto nao foram informados numeros validos

    try:
        r = div(n1,n2)
    except ZeroDivisionError: # exceção específica
        print('Não é possível dividir por zero!')
    except: # exceção geral, qq erro
        print('Ocorreu um erro desconhecido')
    else: # se não der erro, mostra o resultado da divisão
        print(f'Resultado: {r}')
    finally: # bloco que sempre será executado
        print('\nFim do cálculo"')






