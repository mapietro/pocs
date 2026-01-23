# sintaxe
#print(objetos, argumentos)

# mensagem = 'função print()'
# print(mensagem)
# print('aula de python')

# nome = 'Marcio'
# canal = 'youtube'
# print(canal, 'Jazz - ', nome)

# nome = input('Digite seu nome: ')
# print('Olá ' + nome + '! Bem vindo ao curso de Python' )
# print('outro texto')

# print('imprime uma mensagem e muda de linha')
# # usando o end, não quebra a linha no proximo print
# print('imprime uma mensagem e permanece na linha',end='') 
# print(' ...continuo na mesma linha')

# nome = 'Maria'
# idade = 30
# msg_formatada = 'O nome dela é {0} e ela tem {1} anos'.format(nome,idade)
# print(msg_formatada)

# nome = "Giulia"
# idade = 22
# print('O nome dela é {0} e ela tem {1} anos'.format(nome,idade))

nome = 'Fabio'
peso = 73.5
#usando fString
msg = f'Olá, meu nome é {nome} e eu peso {peso} quilos.'
print(msg)

print(f'Olá, meu nominho é  {nome} e eu peso {peso} arrobas')

a = 10
b = 5
res = f'A soma de {a} com {b} é igual a {a+b}'
print(res)

valor = 125.573337
print(f'o valor é \'{valor:.2f}\'')

nome = 'João'
idade = 32
print(f'nome {nome}\tIdade: {idade}')
