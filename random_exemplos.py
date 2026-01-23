import random

## valor = random.randint(1,20)
## print(valor)

# print('Gerar cinco numero aleatorios entre 1 e 50: \n')
# for i in range(5):
#     n = random.randint(1,50)
#     print(f'Número Gerado {n}')

# valor = random.random()
# print(f'Numero gerado: {valor *10:.2f}')

# valor = random.random()
# print(f'Numero gerado:{round(valor *10,2)}')

# dessa forma consigo gerar um numero entre 1 e 100
# valor = random.uniform(1,100)
# print(f'O número gerado é {valor:.2f}')

# escolhe um numero de uma lista
# L = [2,4,6,9,10,13,14,16,18,20,21,27,33]
# n = random.choice(L)
# print(f'Numero escolhido {n}')

# # escolhe X valores de uma litsa
# L = [2,4,6,9,10,13,14,16,18,20,21,27,33]
# n = random.sample(L,3)
# print(f'Numero escolhido {n}')

#embaralhar
L = [2,4,6,9,10,13,14,16,18,20,21,27,33]
print(f'Exibir a lista original: {L}')
print('Embaralhar a lista e exibi-la')
random.shuffle(L)
print(L)
