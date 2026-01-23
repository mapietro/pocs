#sets

# planeta_anao = {'Plutão','Ceres','Eris','Haumea','Makemake'}
# print(planeta_anao)
# print(len(planeta_anao))

# print('Ceres' in planeta_anao)
# print('Lua' in planeta_anao)

# for astro in planeta_anao:
#         print(astro.center(10,'-'))

# astros = ['Lua','Vênus','Sirius','Marte','Lua']
# print(astros, end=' ')
# astro_set = set(astros)
# print(astro_set)

astros1 = {'Lua','Vênus','Sirius','Marte','Io'}
astros2 = {'Lua','Vênus','Sirius','Marte', 'Cometa Halley'}
# print(astros1 == astros2)
# print(astros1 | astros2) # unindo os dois
# print(astros1.union(astros2)) # outro jeito de unir

#intersecao de conjuntos
# print(astros1 & astros2) # interceção dos dois conjuntos
# print(astros1.intersection(astros2)) # outro jeito

# #diferença simetrica de conjuntos
# print(astros1 ^ astros2) # diferença simetrica dos dois conjuntos
# print(astros1.symmetric_difference(astros2)) # outro jeito

astros1.add('Urano')
astros1.add('Sol')
astros1.remove('Io') # se não achar o elemento, da erro
astros1.discard('Crupto') # se não achar o elemento, NÂO da erro
astros1.pop() # elimina um elemente aleatório
astros1.clear() # llimpa tudo
print(astros1)