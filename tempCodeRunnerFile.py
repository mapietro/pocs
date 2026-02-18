
}
"""

from typing import Callable

# O tipo diz: "Aceito qualquer coisa que receba str e retorne bool"
# Não importa se é classe, função, lambda ou método estático.
def processar(dado: str, validador: Callable[[str], bool]) -> None:
    if validador(dado):