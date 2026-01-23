# tuplas são imutaveis
# tuplas são criadas usand0-se parenteses

# tupla = (2,4,6,7,9)
# print(tupla)

halogeneos = ('F','Cl','Br','I','At')
gases_nobres = ('He','Ne','Ar','Xe','Kr','Rn')
#rint(halogeneos)
## print(len(halogeneos))

##print(halogeneos[-1])

elementos = halogeneos + gases_nobres
##print(elementos)

t1 = (5,2,6,8,4,5,6,4,4,0,12,22,3,4,5)
# print(t1.count(5))  #quantas vezes aparece um mesmo item

# print(halogeneos[0:2])

# print(halogeneos[:3])

# print(halogeneos[-2:]) 

# print('Cl' in halogeneos)

# print(sum(t1))

# print(min(t1))
# print(max(t1))

# for elemento in elementos:
#     print(f'Elemeno quimico: {elemento}')

# criando uma lista com base na tuple
# grupo17 = list(halogeneos)
# grupo17[0] = 'H'
# print(grupo17)

# criando uma tupla de uma lista
grupo1 = ['Li','Na','K','Rh','Cs','Fr']
alcalinos = tuple(grupo1)
print(alcalinos)
print(type(alcalinos))

print(sorted(alcalinos))