from pydantic import BaseModel, Field

def eco(a: str | None = None, b: list[str] | None = None) -> None: 
    if a:
        print(f"a = {a}")
    if b:
        print(f"b = {b}")

def somar(a, b, c):
    print(a + b + c)


# Usando pydantic
"""
O Pydantic é uma biblioteca que faz validação automática e conversão de dados baseada em type hints do Python.

Em resumo:

Você define um modelo com tipos (str, int, float, etc.),
e o Pydantic garante que os dados recebidos tenham esses tipos —
convertendo quando possível, e levantando erro se forem inválidos."""

class Usuario(BaseModel):
    nome: str
    idade: int

# usando ... () Os ... (objeto Ellipsis) são um marcador semântico: “esse campo é obrigatório e não tem valor padrão”.
# Nesse caso, se nome não for informado, dá erro de validação.
class Usuario_core(BaseModel):
    nome: str = Field(..., description="Obrigatório")
    idade: int | None = Field(None, description="Opcional")


if __name__ == "__main__":
    eco("teste")
    eco(b=["um", "dois"])
    eco()  # sem argumentos, tudo None


    # Exemplo de criação Pydantic
    # u = Usuario('Márcio',50) --> Dessa forma da erro. O BaseModel (do qual o Usuario herda) não aceita argumentos posicionais, apenas nomeados.
    # O Pydantic não funciona como uma dataclass ou como uma classe comum.
    # Ele faz validação automática dos campos, e por isso exige que os valores sejam passados pelos nomes.

    # Cria o objeto Pydantic passando os parâmetros nomeados, ai funciona
    u = Usuario(nome="Márcio", idade=50)
    print(u)  # mostra Usuario(nome='Márcio', idade=50)
    print(u.model_dump())  # converte para dict {'nome': 'Márcio', 'idade': 50}

    # Dica bônus: Também pode criar o modelo a partir de um dict:
    dados = {"nome": "João", "idade": 30}

    # criando um novo usuário com dados de outro
    u1 = Usuario(nome='Carlos', idade = 20)
    u2 = Usuario(**u1.model_dump())  # copia validado e revalida
    print(u2)

    # O ** serve para expandir um dicionário em argumentos nomeados (keyword arguments) quando você chama uma função ou cria um objeto.
    u = Usuario(**dados)

    # O * faz o mesmo, mas com argumentos posicionais:
    valores = [1, 2, 3]
    somar(*valores)   # equivale a somar(1, 2, 3)

