# escrever em arquivo de textotexto 

# try :
#     manipulador = open('arquivo.txt','w',encoding='utf-8')    
#     manipulador.write('Boson Treinamentos\n')
#     manipulador.write('Como criar um arqvuio de texto com Python')
# except IOError:
#     print('Não foi possível abri o arquivo')
# else:
#     manipulador.close()

# escreve fazendo adição 

# texto = '\nPython é usdo em Ciência de Dados extensivamente'

# try :
#     manipulador = open('arquivo.txt','a',encoding='utf-8')    
#     manipulador.write('\nPython é muito usado em IA')    
#     manipulador.write('\nInteligencia Artificial veio para ficar\n')  
#     manipulador.write(texto)
# except IOError:
#     print('Não foi possível abri o arquivo')
# else:
#     manipulador.close()

#     texto = '\nPython é usdo em Ciência de Dados extensivamente'

frutas = ['Morango\n', 'Uva\n', 'Caju\n', 'Amora\n', 'Framboesa\n', 'Graviola']
try :
    manipulador = open('frutas.txt','w',encoding='utf-8')    
    manipulador.writelines(frutas)        
except IOError:
    print('Não foi possível abri o arquivo')
else:
    manipulador.close()

# Ler o arquivo criado

try:
    manipulador = open('frutas.txt','r',encoding='utf-8')    
    print(manipulador.read())
except IOError:
    print('Não foi possível abri o arquivo')
else:
    manipulador.close()    