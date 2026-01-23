# cria lista
# lista =[2,6,9,4,0,12,3,7]
# for item in lista:
#     print(item)

# palavra = 'Márcio'
# for letra in palavra:
#     print(letra)

# Se eu quiser que o for se repita por X vezes, uso o range para isso
# for numero in range(10): # exemplo só com um numero, vai rodade de 0 a 9
#     print(numero)

# for numero in range(1,10): # exemplo com dois numeros, roda de 1 a 10
#     print(numero)

# nome = input('Digite seu nome: ')
# for x in range(10):
#         print(f'{x+1} {nome}')

# # gera o número de 2 em 2
# for x in range(1,20,2):
#     print(x)

# gera o número de 2 em 2, decremento
# for x in range(20,1,-2):
#     print(x)

pedras = {'Rubi','Esmeralda','Quartzo','Safira','Diamante','Turmalina'}
for pedra in pedras:
    if pedra == 'Quartzo':
        continue
    print(pedra)

pedras = {'Rubi','Esmeralda','Quartzo','Safira','Diamante','Turmalina'}
for pedra in pedras:
    if pedra == 'Quartzo':
        break
    print(f'pedra: {pedra}')

