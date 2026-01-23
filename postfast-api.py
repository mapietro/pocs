
from fastapi import FastAPI, Request                        # FastAPI é o framework; Request para acessar a requisição bruta quando necessário
from fastapi.middleware.cors import CORSMiddleware          # Middleware para CORS (liberação cross-origin)
from fastapi.responses import HTMLResponse, JSONResponse    # Respostas prontas em HTML e JSON
from pydantic import BaseModel, Field                       # BaseModel define modelos Pydantic; Field define metadados/regras de validação
from typing import Optional                                 # Para tipos opcionais (se precisar)
import json                                                 # Para tratar JSON manualmente quando necessário (ex.: erro de parse)
from urllib.parse import parse_qs                           # Para decodificar form-urlencoded (em /enviar-form)

# ------------------------- app e metadados (aparecem no /docs) -------------------------
app = FastAPI(                                         # Cria a aplicação FastAPI
    title="API com CORS — FastAPI",                    # Título exibido no Swagger (/docs) e no OpenAPI
    version="1.0.0",                                   # Versão da API (aparece no /docs)
    description="Exemplo com CORS, JSON via Pydantic e FORM.",  # Descrição opcional
)

# ------------------------- CORS -------------------------
ALLOWED_ORIGINS = ["*"]                                # Em dev, pode deixar "*"; em prod, liste domínios (ex.: ["http://localhost:3000"])
app.add_middleware(                                    # Adiciona o middleware de CORS na app
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,                     # Quem pode acessar
    allow_credentials=False,                           # True se precisar enviar cookies/autorização cross-origin
    allow_methods=["GET", "POST", "OPTIONS"],          # Métodos permitidos
    allow_headers=["Content-Type", "Authorization"],   # Headers permitidos
)

# ------------------------- Pydantic model (aparece no schema do Swagger) -------------------------
class Mensagem(BaseModel):                             # Define o "contrato" de entrada do JSON
    nome: str = Field(..., min_length=1, max_length=50, description="Nome de quem envia")  # Campo obrigatório (...) Os três pontos significam campos obrigatórios, com validações
    mensagem: str = Field(..., min_length=1, max_length=280, description="Texto da mensagem") # Campo obrigatório com limites

    # Exemplo que aparece no /docs (OpenAPI)
    model_config = {                                   # Para Pydantic v2; se estiver em v1, use Config + schema_extra
        "json_schema_extra": {
            "example": {                               # O Swagger mostra este exemplo no body
                "nome": "Márcio",
                "mensagem": "Olá via JSON!"
            }
        }
    }

# ------------------------- Rotas -------------------------
@app.get("/", response_class=HTMLResponse)             # Rota GET raiz, devolvendo HTML
async def home():
    # HTML simples com instruções: form POST e curl com JSON
    html = """
    <html>
      <body>
        <h2>Teste de POST (form e JSON) com CORS — FastAPI</h2>

        <h3>Form (application/x-www-form-urlencoded)</h3>
        <!-- este form envia para /enviar-form (rota específica para form) -->
        <form action="/enviar-form" method="post">
          <label>Nome:</label><br>
          <input type="text" name="nome"><br><br>
          <label>Mensagem:</label><br>
          <textarea name="mensagem"></textarea><br><br>
          <button type="submit">Enviar</button>
        </form>

        <hr>

        <h3>JSON (application/json)</h3>
        <p>Use o Swagger em <a href="/docs" target="_blank">/docs</a> e teste o <b>POST /enviar</b> com o corpo JSON.</p>
        <pre>
curl -X POST http://localhost:8000/enviar \\
  -H "Content-Type: application/json" \\
  -d '{"nome":"Marcio","mensagem":"Olá via JSON"}'
        </pre>

        <hr>
        <h3>GET /eco?a=1&b=2&b=3</h3>
        <a href="/eco?a=1&b=2&b=3">Testar /eco</a>
      </body>
    </html>
    """
    return HTMLResponse(content=html)                  # Retorna HTML; FastAPI define Content-Type automaticamente

@app.get("/eco")                                      # Rota GET /eco
async def eco(request: Request):                      # Recebe o objeto Request para acessar query params
    qp = request.query_params                         # query_params é um MultiDict imutável
    # A resposta abaixo preserva todas as ocorrências (getlist) -> {"a":["1"], "b":["2","3"]}
    return JSONResponse({"query": {k: qp.getlist(k) for k in qp}})

# ------------------------- POST /enviar (JSON com validação Pydantic) -------------------------
@app.post(
    "/enviar",                                        # Caminho da rota
    response_model=dict,                              # Opcional: dica do tipo de resposta (o FastAPI montará o schema simples)
    summary="Recebe JSON validado por Pydantic",      # Texto curto que aparece no /docs
    description="Envia um JSON com campos 'nome' e 'mensagem'. Validação automática via Pydantic.", # Descrição detalhada
)
async def enviar(payload: Mensagem):                  # Aqui está a mágica: 'payload' é um modelo Pydantic; o FastAPI valida antes de chamar a função
    # Se o JSON não bater com o schema (ex.: faltou 'mensagem' ou tipos errados),
    # o FastAPI responde automaticamente 422 com detalhes de validação e NÃO entra aqui.

    # payload é um objeto Python do tipo Mensagem, com atributos já convertidos/validados:
    # payload.nome (str), payload.mensagem (str)
    print('Passou por aqui')
    return {                                          # Retornando um dict simples; o FastAPI serializa como JSON
        "ok": True,
        "tipo": "json",
        "recebido": payload.model_dump(),             # Em Pydantic v2, use model_dump(); em v1 seria payload.dict()
    }

# ------------------------- POST /enviar-form (form-urlencoded para o formulário HTML) -------------------------
@app.post("/enviar-form", response_class=HTMLResponse)# Caminho separado só para processar formulário HTML
async def enviar_form(request: Request):              # Usamos Request para ler o body bruto do form
    # Detecta content-type (não é obrigatório aqui, mas útil se quiser validar)
    content_type = (request.headers.get("content-type") or "").split(";")[0].strip().lower()

    if content_type != "application/x-www-form-urlencoded":
        # Se o form não veio no formato esperado, responde 415
        return HTMLResponse(
            content=f"<p>Content-Type nao suportado: {content_type or 'desconhecido'}</p>",
            status_code=415
        )

    # Lê o corpo (bytes) e decodifica
    form_bytes = await request.body()                 # Lê todo o corpo do request (bytes)
    data = parse_qs(form_bytes.decode("utf-8"))       # parse_qs -> dict de listas: {"nome":["..."], "mensagem":["..."]}

    # Extrai os campos (pegando o primeiro valor de cada lista)
    nome = (data.get("nome") or [""])[0]
    mensagem = (data.get("mensagem") or [""])[0]

    # Monta uma resposta HTML amigável
    html = f"""
    <html>
      <body>
        <h2>Dados recebidos (FORM) — FastAPI</h2>
        <p><b>Nome:</b> {nome}</p>
        <p><b>Mensagem:</b> {mensagem}</p>
        <a href="/">Voltar</a>
      </body>
    </html>
    """
    return HTMLResponse(content=html)                 # Retorna HTML de confirmação

# uvicorn postfast-api:app --reload
