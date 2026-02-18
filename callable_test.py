"""
Docstring for callable_test Example in Java for reference
// 1. O Contrato
public interface Validador {
    boolean validar(String dado);
}

// 2. O Consumidor
public class Servico {
    public void processar(String dado, Validador validador) { // Polimorfismo
        if (validador.validar(dado)) { ... }
    }
}
"""

from typing import Callable

# O tipo diz: "Aceito qualquer coisa que receba str e retorne bool"
# Não importa se é classe, função, lambda ou método estático.
def processar(dado: str, validador: Callable[[str], bool]) -> None:
    if validador(dado):
        print("Passou legal!")

# Uso: Passo a função direto. Sem 'new ValidadorImpl()
def minha_regra(s: str) -> bool:
    return len(s) >= 5

processar("iJazz", minha_regra)


