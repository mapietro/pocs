# existem escopo global e local
# local acessado só no escopo da função
# global acessado a todo o ambiente

var_global = 'Curso completo de Python'

def escreve_texto():
    var_local = 'Márcio Di Pietro'

    ##global var_global # com essa instrução, aviso que a variavel que quero acessar é a global, sem isso ela se torna local
    var_global = 'qualquer coisa' ## Essa variável será lida no escopo da função
    print(f'Váriavel GLobal {var_global}')
    print(f'Váriavel Local {var_local}')

if __name__ == '__main__':
    print('Executar a função escreve texto()')
    escreve_texto()

    print('Tentar acessar as variaveis diretamente')
    print(f'Váriavel GLobal em Main {var_global}') ## Essa variável será a global
   
