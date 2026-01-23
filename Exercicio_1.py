
Bebidas = []

print("Olá, escolha cinco bebidas que mais gosta")

for i in range(5):
    print(f'Infome o nome da sua bebida número{i} :\n')
    item = input()
    Bebidas.append(item)

Bebidas.sort()
print('\nBebidas Escolhidas')
for bebida in Bebidas:
    print(bebida)

print('\nCerSaude')


 
