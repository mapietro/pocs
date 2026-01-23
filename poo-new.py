from __future__ import annotations
from typing import Optional

class Veiculo:
    #-> None indica que o método não retorna nada.
    def __init__(self, fabricante: str, modelo: str) -> None:
        self._fabricante: str = fabricante
        self._modelo: str = modelo
        self._num_registro: Optional[str] = None

    def movimentar(self) -> None: # -> None indica que o método não retorna nada.
        print("Sou um veículo e me desloco")

    @property
    def fabricante(self) -> str:
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

    def movimentar(self) -> None:
        print("Sou um avião e voo pelos céus")


if __name__ == "__main__":
    meu_veiculo = Veiculo("GM", "Cadillac Escalade")  # (pequeno typo: Escalade)
    meu_veiculo.movimentar()
    meu_veiculo.num_registro = "490321-1"
    print(f"registro: {meu_veiculo.num_registro}")
    print(meu_veiculo.modelo)
    print(meu_veiculo.fabricante)

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
