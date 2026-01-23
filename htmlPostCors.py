from wsgiref.simple_server import make_server
from urllib.parse import parse_qs
import json

# =========================
# Configuração de CORS
# =========================
# Em DEV, use "*".
# Em PRODUÇÃO, liste domínios permitidos, ex.: {"https://meusite.com", "https://app.meusite.com"}
ALLOWED_ORIGINS = {"*"}  # {"http://localhost:3000"}  # exemplo restrito

ALLOWED_METHODS = "GET, POST, OPTIONS"
ALLOWED_HEADERS = "Content-Type, Authorization"  # adicione o que precisar
ALLOW_CREDENTIALS = False  # True se precisar enviar cookies/autorização cross-origin

def cors_headers(environ):
    origin = environ.get("HTTP_ORIGIN")
    # Se estiver com "*", devolve *; senão, somente a origin se estiver permitida
    if "*" in ALLOWED_ORIGINS:
        allow_origin = "*"
    elif origin in ALLOWED_ORIGINS:
        allow_origin = origin
    else:
        allow_origin = "null"  # navegador vai bloquear

    headers = [
        ("Access-Control-Allow-Origin", allow_origin),
        ("Access-Control-Allow-Methods", ALLOWED_METHODS),
        ("Access-Control-Allow-Headers", ALLOWED_HEADERS),
    ]
    if ALLOW_CREDENTIALS:
        headers.append(("Access-Control-Allow-Credentials", "true"))
        # IMPORTANTE: com credentials=true, o Allow-Origin NÃO pode ser "*"
    return headers

# =========================
# Helpers de resposta
# =========================
def respond(start_response, status, body_bytes, content_type="text/plain; charset=utf-8", extra_headers=None):
    headers = [
        ("Content-Type", content_type),
        ("Content-Length", str(len(body_bytes))),
    ]
    if extra_headers:
        headers.extend(extra_headers)
    start_response(status, headers)
    return [body_bytes]

def respond_html(start_response, html_str, extra_headers=None):
    return respond(start_response, "200 OK", html_str.encode("utf-8"), "text/html; charset=utf-8", extra_headers)

def respond_json(start_response, data, status="200 OK", extra_headers=None):
    body = json.dumps(data, ensure_ascii=False).encode("utf-8")
    return respond(start_response, status, body, "application/json; charset=utf-8", extra_headers)

def respond_404(start_response, extra_headers=None):
    return respond(start_response, "404 Not Found", b"Rota nao encontrada", extra_headers=extra_headers)

def respond_400(start_response, msg="Requisicao invalida", extra_headers=None):
    return respond_json(start_response, {"error": msg}, status="400 Bad Request", extra_headers=extra_headers)

def respond_415(start_response, msg="Tipo de conteudo nao suportado", extra_headers=None):
    return respond_json(start_response, {"error": msg}, status="415 Unsupported Media Type", extra_headers=extra_headers)

# =========================
# Aplicação WSGI
# =========================
def application(environ, start_response):
    path = environ.get("PATH_INFO", "/")
    method = environ.get("REQUEST_METHOD", "GET")
    cors = cors_headers(environ)

    # Trate o preflight OPTIONS para QUALQUER rota que suporte cross-origin
    if method == "OPTIONS":
        # Sem corpo (204). Alguns clientes esperam também Max-Age:
        cors.append(("Access-Control-Max-Age", "86400"))
        return respond(start_response, "204 No Content", b"", extra_headers=cors)

    # ---------- GET / ----------
    if path == "/" and method == "GET":
        html = """
        <html>
          <body>
            <h2>Teste de POST (form e JSON) com CORS</h2>
            <h3>Form (application/x-www-form-urlencoded)</h3>
            <form action="/enviar" method="post">
              <label>Nome:</label><br>
              <input type="text" name="nome"><br><br>
              <label>Mensagem:</label><br>
              <textarea name="mensagem"></textarea><br><br>
              <button type="submit">Enviar</button>
            </form>

            <hr>

            <h3>JSON (application/json)</h3>
            <p>curl:</p>
            <pre>
curl -X POST http://localhost:8000/enviar \
  -H "Content-Type: application/json" \
  -d '{"nome":"Marcio","mensagem":"Olá via JSON"}'
            </pre>

            <hr>

            <h3>GET /eco?a=1&b=2&b=3</h3>
            <a href="/eco?a=1&b=2&b=3">Testar /eco</a>
          </body>
        </html>
        """
        return respond_html(start_response, html, extra_headers=cors)

    # ---------- GET /eco ----------
    if path == "/eco" and method == "GET":
        qs = parse_qs(environ.get("QUERY_STRING", ""))
        return respond_json(start_response, {"query": qs}, extra_headers=cors)

    # ---------- POST /enviar ----------
    if path == "/enviar" and method == "POST":
        content_type = environ.get("CONTENT_TYPE", "").split(";")[0].strip().lower()
        try:
            length = int(environ.get("CONTENT_LENGTH", 0))
        except ValueError:
            length = 0

        raw_body = environ["wsgi.input"].read(length) if length > 0 else b""

        # JSON
        if content_type == "application/json":
            if not raw_body:
                return respond_400(start_response, "Corpo JSON vazio", extra_headers=cors)
            try:
                payload = json.loads(raw_body.decode("utf-8"))
            except json.JSONDecodeError:
                return respond_400(start_response, "JSON invalido", extra_headers=cors)

            nome = payload.get("nome", "")
            mensagem = payload.get("mensagem", "")
            return respond_json(start_response, {
                "ok": True,
                "tipo": "json",
                "recebido": {"nome": nome, "mensagem": mensagem}
            }, extra_headers=cors)

        # Form
        if content_type == "application/x-www-form-urlencoded":
            data = parse_qs(raw_body.decode("utf-8"))
            nome = data.get("nome", [""])[0]
            mensagem = data.get("mensagem", [""])[0]
            html = f"""
            <html>
              <body>
                <h2>Dados recebidos (FORM)</h2>
                <p><b>Nome:</b> {nome}</p>
                <p><b>Mensagem:</b> {mensagem}</p>
                <a href="/">Voltar</a>
              </body>
            </html>
            """
            return respond_html(start_response, html, extra_headers=cors)

        return respond_415(start_response, f"Content-Type nao suportado: {content_type or 'desconhecido'}", extra_headers=cors)

    # ---------- 404 ----------
    return respond_404(start_response, extra_headers=cors)

# =========================
# Runner
# =========================
if __name__ == "__main__":
    with make_server("0.0.0.0", 8000, application) as httpd:
        print("Servidor WSGI (CORS) em http://localhost:8000")
        httpd.serve_forever()
