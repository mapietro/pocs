# make_server cria um servidor WSGI mínimo para desenvolvimento.
from wsgiref.simple_server import make_server
# parse_qs ajuda a decodificar a query string (?a=1&b=2).
from urllib.parse import parse_qs

# A aplicação WSGI é uma função que recebe:
# - environ: dicionário com informações da requisição (headers, caminho, método, etc.).
# - start_response: função de callback para iniciar a resposta (status e headers).
def application(environ, start_response):
    # Obtém o caminho requisitado (ex.: "/", "/eco").
    path = environ.get("PATH_INFO", "/")
    # Obtém o método HTTP (GET, POST, ...).
    method = environ.get("REQUEST_METHOD", "GET")

    # Rota raíz (GET /) responde com texto simples.
    if path == "/" and method == "GET":
        # Inicia a resposta com código 200 e header Content-Type texto/UTF-8.
        start_response("200 OK", [("Content-Type", "text/plain; charset=utf-8")])
        # Corpo da resposta é um iterável de bytes (lista com um item).
        return [b"Hello, WSGI!"]

    # Rota /eco (GET /eco?x=1&x=2) devolve a query string decodificada.
    if path == "/eco" and method == "GET":
        # Lê a query string crua (tudo após '?').
        raw_qs = environ.get("QUERY_STRING", "")
        # Converte para dict: {"x": ["1", "2"]}.
        qs = parse_qs(raw_qs)
        # Inicia a resposta com 200 e Content-Type texto/UTF-8.
        start_response("200 OK", [("Content-Type", "text/plain; charset=utf-8")])
        # Converte o dict para string e envia como bytes.
        return [str(qs).encode("utf-8")]

    # Se não encontrou rota, retorna 404.
    start_response("404 Not Found", [("Content-Type", "text/plain; charset=utf-8")])
    return [b"Rota nao encontrada"]

# Ponto de entrada.
if __name__ == "__main__":
    # Cria o servidor WSGI escutando em 0.0.0.0:8000 e servindo a função 'application'.
    with make_server("0.0.0.0", 8000, application) as httpd:
        # Log simples da URL.
        print("WSGI em http://localhost:8000")
        # Loop de serviço infinito.
        httpd.serve_forever()

        
