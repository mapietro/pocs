# classes e objetos

class Veiculo:
    def __init__(self, fabricante, modelo): # construtor da classe
        # estes atributos estão publicos
        # self.fabricante = fabricante 
        # self.modelo = modelo
        # self.num_registro = None

        # estes atributos são privados. por usar dois underscore ante do nome
        self.__fabricante = fabricante 
        self.__modelo = modelo
        self.__num_registro = None

    def movimentar(self):
        print('Sou um veículo e me desloco')

    def getFabricante(self):
        return(self.__fabricante)
    
    def getModelo(self):
        return(self.__modelo)
    
    def setNumRegistro(self, registro):
        self.__num_registro = registro

    def getRegistro(self):
        return self.__num_registro
    
class Carro(Veiculo):
    # método contrutor será herdado

    def movimentar(self):
        print('Sou um carro e ando pelas ruas')

class Aviao(Veiculo):

    def __init__(self, fabricante, modelo, categoria):
        super().__init__(fabricante, modelo)
        self.__categoria = categoria

    def getCategoria(self):
        return(self.__categoria)
    
    def movimentar(self):
        print('Sou um avião e voo pelos céus')

if __name__ == '__main__':
    meu_veiculo = Veiculo('GM','Cadillac Escalate')
    meu_veiculo.movimentar()

    meu_veiculo.setNumRegistro('490321-1')
    print(f'registro: {meu_veiculo.getRegistro()}')

    print(meu_veiculo.getModelo())
    print(meu_veiculo.getFabricante())

    meu_carro = Carro('Volkswagen','Polo')
    print('novo carro'.center(20, "-")) # Alinha a palavra ao meio com tracinhos a direita e esqueda
    meu_carro.movimentar()
    print(f'Fabricante: {meu_carro.getFabricante()}')
    print(f'Modelo: {meu_carro.getModelo()}')
    meu_carro.setNumRegistro('897776-9')
    print(f'Registro: {meu_carro.getRegistro()}')

    meu_aviao = Aviao('Boeing','777','Comercial')
    print('novo avião'.center(20, "-")) # Alinha a palavra ao meio com tracinhos a direita e esqueda
    meu_aviao.movimentar()
    print(f'Fabricante: {meu_aviao.getFabricante()}')
    print(f'Modelo: {meu_aviao.getModelo()}')
    meu_aviao.setNumRegistro('AA9899PK')
    print(f'Registro: {meu_aviao.getRegistro()}')
    print(f'Categoria: {meu_aviao.getCategoria()}')