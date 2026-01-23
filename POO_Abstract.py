from __future__ import annotations
from abc import ABC, abstractmethod
from typing import Optional

class Veiculo(ABC): # Herda de ABC para dizer que é uma classe Abstrata
    # Em Python, esse : str não impõe uma restrição real 
    # — ele apenas declara a intenção de que aquele parâmetro 
    # deveria ser uma string.
    def __init__(self, fabricante: str, modelo: str) -> None:
        self._fabricante: str = fabricante
        self._modelo: str = modelo
        self._num_registro: Optional[str] = None

    # --- contrato a ser implementado pelas subclasses ---
    @abstractmethod
    def movimentar(self) -> None:
        """Cada veículo deve descrever como se movimenta."""
        ...

    # --- properties comuns a todo veículo ---
    @property
    def fabricante(self) -> str: # -> indica que o ideal é retornar uma String
        return self._fabricante

    @property
    def modelo(self) -> str:
        return self._modelo

    @property
    def num_registro(self) -> Optional[str]:
        return self._num_registro

    @num_registro.setter
    def num_registro(self, valor: str) -> None:
        self._num_registro = valor

    def __str__(self) -> str:
        return f"{self.__class__.__name__}(fabricante={self._fabricante}, modelo={self._modelo})"

# sou obrigado a imeplementar o método abstrato: movimentar
# caso não implemente, tere um erro
class Carro(Veiculo): 
    def movimentar(self) -> None:
        print("Sou um carro e ando pelas ruas")



class Aviao(Veiculo):
    def __init__(self, fabricante: str, modelo: str, categoria: str) -> None:
        super().__init__(fabricante, modelo)
        self._categoria: str = categoria

    @property
    def categoria(self) -> str:
        return self._categoria

    # sou obrigado a imeplementar o método abstrato: movimentar
    # caso não implemente, tere um erro
    def movimentar(self) -> None:
        print("Sou um avião e voo pelos céus")


if __name__ == "__main__":
    # ATENÇÃO: Veiculo agora é abstrata → não pode ser instanciada.
    # meu_veiculo = Veiculo("GM", "Cadillac Escalade")  # Isso daria erro!

    meu_carro = Carro("Volkswagen", "Polo")
    print("novo carro".center(20, "-"))
    meu_carro.movimentar()
    print(f"Fabricante: {meu_carro.fabricante}")
    print(f"Modelo: {meu_carro.modelo}")
    meu_carro.num_registro = "897776-9"
    print(f"Registro: {meu_carro.num_registro}")

    meu_aviao = Aviao("Boeing", "777", "Comercial")
    print("novo avião".center(20, "-"))
    meu_aviao.movimentar()
    print(f"Fabricante: {meu_aviao.fabricante}")
    print(f"Modelo: {meu_aviao.modelo}")
    meu_aviao.num_registro = "AA9899PK"
    print(f"Registro: {meu_aviao.num_registro}")
    print(f"Categoria: {meu_aviao.categoria}")
    print(meu_aviao.__str__())
