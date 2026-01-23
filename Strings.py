# nome = 'Márcio'
# sobreNome = 'Di Pietro'
# letra = nome[2]
# print(letra)
# print(len(nome))

# print(nome +' '+ sobreNome)

# frase = 'Vamos aprender Python hoje'
# # palavras = frase.split()
# # print(palavras)
# # print(palavras[1])

# # for palavra in palavras:
# #     print(palavra)

# # for letra in frase:
# #     print(letra)

# print(frase[0:5])
# print(frase[6:15])

# print(frase[-3:])

# email = input('Digite seu endereço de email')
# arroba = email.find('@')
# print(arroba)
# usuario = email[0:arroba]
# dominio = email[arroba+1:]
# print(usuario)
# print(dominio)

# produtos = 'carbonato de sódio e óxido de zinco'
# print('sódio' in produtos)
# print('magnézio' not in produtos)

# item = 'hipoclorito'
# pos = item.find('clor')
# print(pos)
# pos = item.find('flu')
# print(pos)

# objeto_celeste = 'galaxia esPiral M31'
# print(objeto_celeste.upper())
# print(objeto_celeste.lower())
# print(objeto_celeste.capitalize())
# print(objeto_celeste.title())

# suplemento = 'cloreto de magnésio'
# n_suplemento = suplemento.replace('magnésio','zinco')
# print(suplemento)
# print(n_suplemento)

# frase = '      Ômega 3 é bom para a saúde!     '
# print(frase)
# print(frase.lstrip())
# print(frase.rstrip())
# print(frase.strip())

fruta = 'Abacate'
print(fruta)
# print(fruta.rjust(20)) # Alinha a palavra a direita após 20 espaços
#print(fruta.center(20)) # Alinha a palavra ao meio com espaços a direita e esqueda
# print(fruta.ljust(20)) # Alinha a palavra a esquerda após 20 espaços

# print(fruta.ljust(20, "-")) # Alinha a palavra a esquerda após 20 tracinhos
print(fruta.center(20, "-")) # Alinha a palavra ao meio com tracinhos a direita e esqueda

# p = 'Boson Treinamentos'
# print(p.startswith('Bo'))
# print(p.startswith('b'))
# print(p.endswith('s'))
# print(p.endswith('o'))

#DocStrings
"""
Docstring é uma espécie de documentação que 
podemos inserir dentro de um mófulo, função
ou classe no Python, entre outros locais.
    Respeita deslocamento do textoe é   multilinhas    

"""


texto = """
Docstring é uma espécie de documentação que 
podemos inserir dentro de um mófulo, função
ou classe no Python, entre outros locais.
    Respeita deslocamento do textoe é   multilinhas 
Use somente para documentar classe e métodos, e não
como comentários   

"""
print(texto)
