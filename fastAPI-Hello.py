from fastapi import FastAPI

# Cria a aplicação FastAPI
app = FastAPI()

# ---------- ROTA 1 ----------
@app.get("/")
def home():
    return {"mensagem": "Olá, FastAPI está funcionando!"}

# ---------- ROTA 2 ----------
@app.get("/eco")
def eco(a: str = "", b: str = ""):
    return {"a": a, "b": b}

# ---------- ROTA 3 ----------
@app.post("/enviar")
def enviar():
    return {"ok": True, "mensagem": "Recebi seu POST!"}

# uvicorn fastAPI-Hello:app --host 0.0.0.0 --port 8000 --reload
