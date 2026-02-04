# Auth Module (Session Cookie + CSRF) — Arquitetura e Execução

Este repositório (ou módulo) implementa um sistema de autenticação **API-first** com:

- **Sessão stateful** (token opaco via cookie HttpOnly + persistência no banco)
- **CSRF protection** via **Double Submit Cookie**
- **Logout e revogação**
- **Troca de senha com revogação total**
- **Rate limit / lockout** (in-memory, ideal para 1 worker no início)
- Separação arquitetural: **Controllers → Services → Repositories → Models/Schemas/Deps**

O objetivo é ser um **padrão reutilizável** para projetos internos (ex.: dashboards) e também evoluir para usuários comuns (signin/signup) sem refazer o core de segurança.

---

## 1) Conceitos (modelo mental)

### 1.1 Autenticação vs Sessão
- **Autenticação (login)**: prova identidade (usuário + senha).
- **Sessão**: mantém identidade “viva” entre requests.

Após o login, o backend cria uma sessão e o browser passa a enviar automaticamente o cookie de sessão em cada request.

### 1.2 Por que cookie HttpOnly?
O cookie de sessão (`ijazz_session` no exemplo) é **HttpOnly**:
- JavaScript não consegue ler o cookie.
- Reduz muito o risco em caso de XSS (roubo de token).

### 1.3 CSRF (Double Submit Cookie)
Como o browser envia cookies automaticamente, precisamos provar “intenção” em requisições mutáveis (POST/PUT/PATCH/DELETE).

Estratégia **Double Submit Cookie**:
- Um cookie `csrf` (não HttpOnly) é setado pelo backend.
- O frontend lê esse cookie e envia o mesmo valor no header `X-CSRF-Token`.
- O backend valida: **cookie == header**.

**CSRF é exigido para mutações**, exceto login (porque no login ainda não há sessão estabelecida).

### 1.4 Revogação total (troca de senha derruba todas as sessões)
Além de revogar sessões individualmente, existe um mecanismo de **revogação total**:

- O usuário possui um `auth_version_token` (“versão” da identidade).
- Cada sessão guarda um snapshot (`user_auth_version_snapshot`) do token atual.
- Se o usuário trocar senha, o backend **rotaciona** `auth_version_token`.
- Sessões antigas ficam inválidas imediatamente (snapshot não bate mais).

Isso garante que:
- Ao trocar senha, você derruba sessões em outros dispositivos.
- Você evita “sessões fantasma” após mudança de credencial.

### 1.5 Rate limit / Lockout (anti brute-force)
Implementado como `InMemoryLoginThrottle`:
- Chave típica: `username:ip`
- Exemplo: 5 falhas em 10 min → lock por 5 min

Para 1 worker, memória é suficiente.
Ao escalar, evolui para Redis/DB mantendo a interface.

---

## 2) Arquitetura (camadas e responsabilidades)

### 2.1 Estrutura sugerida

```text
app/
  api/
    auth_controller.py         # Rotas HTTP /auth/*
  services/
    auth_service.py            # Regras de negócio (sem FastAPI)
  db/
    models/
      user.py                  # SQLAlchemy User
      session.py               # SQLAlchemy Session
    repositories/
      auth_repository.py       # Queries/CRUD (sem regra de negócio)
  schemas/
    auth/
      api.py                   # DTOs Pydantic (request/response)
  core/
    password.py                # Argon2 hash/verify
    csrf.py                    # CSRF double submit helpers
    throttle.py                # lockout/rate limit (in-memory)
  deps/
    auth.py                    # dependencies + DI (require_user, require_csrf)

2.2 Regras de ouro

Controllers: apenas HTTP (entrada/saída), cookies, status codes, DTOs.

Services: regras de negócio (login, validação, revogação, troca de senha).
Service não conhece FastAPI.

Repositories: acesso a dados (SQLAlchemy).
Sem regra de negócio.

Models: persistência e constraints.

Schemas: contrato externo da API (Pydantic).

Deps: composição (injeção) e guards (require_user, require_csrf).

3) Contrato HTTP (endpoints)
3.1 CSRF

GET /auth/csrf

Seta cookie csrf (não HttpOnly)

O frontend passa a usar X-CSRF-Token em mutações

3.2 Login

POST /auth/login

Body: { "username": "...", "password": "..." }

Se sucesso:

seta cookie ijazz_session (HttpOnly)

retorna { "ok": true }

3.3 Sessão atual

GET /auth/me

Requer sessão válida

Retorna { "username": "..." }

3.4 Logout

POST /auth/logout (CSRF obrigatório)

Revoga sessão e limpa cookie

Idempotente (se já expirou, ainda funciona)

3.5 Trocar senha

POST /auth/change-password (CSRF obrigatório)

Body: { "current_password": "...", "new_password": "..." }

Troca senha + revoga todas as sessões do usuário

4) Configuração (ENV)

Exemplos (ajuste nomes conforme seu projeto):

# App
ENV=development

# Session
AUTH_SESSION_COOKIE_NAME=ijazz_session
AUTH_SESSION_TTL_HOURS=12

# Cookies (produção)
AUTH_COOKIE_SECURE=true
AUTH_COOKIE_SAMESITE=lax
AUTH_COOKIE_PATH=/

# CSRF
AUTH_CSRF_COOKIE_NAME=csrf

# DB
DATABASE_URL=postgresql+asyncpg://user:pass@localhost:5432/app


5) Banco de dados e Migrations (Alembic)
5.1 Criar tabelas

As tabelas mínimas:

users

sessions

Se o projeto usa Alembic:

alembic revision --autogenerate -m "create users and sessions"
alembic upgrade head


Se já existe pipeline de migração, apenas rode:

alembic upgrade head

6) Como rodar localmente
6.1 Subir Postgres (Docker)

Exemplo rápido:

docker run --name auth-postgres \
  -e POSTGRES_PASSWORD=postgres \
  -e POSTGRES_USER=postgres \
  -e POSTGRES_DB=app \
  -p 5432:5432 \
  -d postgres:16


Configure DATABASE_URL conforme acima.

6.2 Instalar dependências (exemplo)
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

6.3 Rodar migrations
alembic upgrade head

6.4 Rodar API
uvicorn app.main:app --reload --port 8000

7) Testando com curl (passo a passo)

Dica: use -c cookies.txt -b cookies.txt para persistir cookies.

7.1 Obter CSRF cookie
curl -i -c cookies.txt http://localhost:8000/auth/csrf


Pegue o cookie csrf do cookies.txt.

7.2 Login
curl -i -c cookies.txt -b cookies.txt \
  -H "Content-Type: application/json" \
  -d '{"username":"pietro","password":"senha123"}' \
  http://localhost:8000/auth/login


Isso deve setar o cookie ijazz_session.

7.3 /me
curl -i -b cookies.txt http://localhost:8000/auth/me

7.4 Logout (CSRF obrigatório)

Você precisa enviar o header com o mesmo valor do cookie csrf:

CSRF=$(grep csrf cookies.txt | awk '{print $7}')
curl -i -b cookies.txt -c cookies.txt \
  -H "X-CSRF-Token: $CSRF" \
  -X POST http://localhost:8000/auth/logout

7.5 Change password (CSRF obrigatório)
CSRF=$(grep csrf cookies.txt | awk '{print $7}')
curl -i -b cookies.txt -c cookies.txt \
  -H "Content-Type: application/json" \
  -H "X-CSRF-Token: $CSRF" \
  -d '{"current_password":"senha123","new_password":"novaSenha@123"}' \
  -X POST http://localhost:8000/auth/change-password


Após trocar senha:

sessões antigas devem cair

login com senha antiga deve falhar

8) Integração com Frontend (SPA)
8.1 Regras do fetch

Sempre usar credentials: 'include'

Para mutações, enviar X-CSRF-Token com o valor do cookie CSRF

Fluxo típico:

GET /auth/csrf ao iniciar a app (ou antes de mutações)

POST /auth/login

GET /auth/me para popular AuthContext

POST /auth/logout e limpar estado

8.2 AuthContext + AuthGuard

AuthContext centraliza:

user, isAuthenticated, isLoading, login, logout, refreshMe

AuthGuard protege rotas privadas

9) Segurança e produção (checklist)

 Cookies com Secure=true e HTTPS

 SameSite=Lax (ou Strict se aplicável)

 HttpOnly no cookie de sessão

 CSRF obrigatório em mutações

 Rate limit/lockout no login

 Troca de senha revoga sessões

 Nunca logar senha/hash/tokens

 Auditoria mínima (login, logout, change-password)

10) Evolução (usuários comuns e signup)

Para suportar signup:

adicionar endpoint POST /auth/register

criar usuário (users) com password_hash

decidir se auto-login acontece ou não

O core não muda:

sessão cookie

CSRF

revogação

AuthContext/AuthGuard