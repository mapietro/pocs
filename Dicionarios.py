# Dicionarios

elemento = {
    'Z': 3,
    'nome' : 'Lítio',
    'grupo' : 'Metais Alcalinos',
    'densidade' : 0.534
}

# print(f'elemeento:  {elemento['nome']}')
# print(f'Densidade:  {elemento['densidade']}')
# print(f'O dicionário possui: {len(elemento)} elementos')

# Atualizar uma entrada do dicionário
# elemento['grupo'] = 'Alcalino'
# print(elemento)

# # Adicionar uma entrada
# elemento['periodo'] = 1
# print(elemento)

# #esclusão de itens em dicionários
# del elemento['periodo']
# print(elemento)

# #apagar todos os itens
# elemento.clear
# print(elemento)

# #apagar totalmnte
# del elemento
# # print(elemento) # vai dar eero pois não existe mais

# print(elemento.items())
# for i in elemento.items():
#     print(i)

# for i in elemento.keys():
#     print(i)

# for i in elemento.values():
#     print(i)

# for i in elemento.keys():
#     print(i)

# for i, j in elemento.items():
#     print(f'{i}: {j}')

# ok = 'nome' in elemento
# print(ok)

# print(elemento.get('nome'))


# Listas com dicionarios

minha_lista = []
meu_dicionario = {"name": "Márcio", "idade": 30}
minha_lista.append(meu_dicionario)

print(hasattr(minha_lista, 'meu_dicionario'))