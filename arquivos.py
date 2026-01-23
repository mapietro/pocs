# manipulação de arquivos de texto



# print(f'\Método read():\n')
#print(manipulador.read()) # le o arquivo inteiro

#print(manipulador.readline()) # le uma linha por vez. Se baseia em \n
#print(manipulador.readline()) # le uma linha por vez. Se baseia em \n

# print(manipulador.readlines()) # le todas as linhas

texto = input('Qual Termo deseja procurar no arquivo? ')

try :
    manipulador = open('arquivo.txt','r',encoding='utf-8')
    for linha in manipulador:
        linha = linha.rstrip() # retira o ultimo caractere da linha, ou seja, o \n
        if texto in linha:
            print(f'A String foi encontrada:\n{linha}')
        else:
            print('String não encontrada')
except IOError:
    print('Não foi possível abri o arquivo')
else:
    manipulador.close()

