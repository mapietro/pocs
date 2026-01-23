import socket

# Cria um socket TCP (AF_INET = IPv4, SOCK_STREAM = TCP).
with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server:
    # Permite reutilizar a porta rapidamente após encerrar (evita TIME_WAIT longo).
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    # Faz o bind do socket no IP 0.0.0.0 (todas as interfaces) e porta 8000.
    server.bind(("0.0.0.0", 8000))
    # Começa a "escutar" conexões; backlog 5 é o número de conexões pendentes permitidas.
    server.listen(5)
    print("Socket HTTP cru em http://localhost:8000")

    while True:
        # Aceita uma conexão (bloqueante); retorna um novo socket e o endereço do cliente.
        conn, addr = server.accept()
        # Usa context manager para garantir fechamento do socket do cliente ao final.
        with conn:
            # Lê até 4096 bytes do request (linha de requisição + headers + possível corpo).
            data = conn.recv(4096)
            # Se nada veio, segue para próxima conexão.
            if not data:
                continue

            # Decodifica os bytes para string (assumindo UTF-8) para parsing simples.
            req = data.decode("utf-8", errors="ignore")
            # A primeira linha do HTTP contém: MÉTODO PATH VERSÃO (ex.: "GET / HTTP/1.1").
            first_line = req.split("\r\n", 1)[0]
            # Faz o split por espaço para separar método e caminho. Tratamento defensivo.
            parts = first_line.split(" ")
            method = parts[0] if len(parts) > 0 else ""
            path = parts[1] if len(parts) > 1 else "/"

            # Roteamento mínimo.
            if method == "GET" and path == "/":
                # Corpo da resposta.
                body = b"Hello, HTTP cru!"
                # Monta a resposta HTTP/1.0: status line + headers + CRLF + body.
                resp = (
                    b"HTTP/1.0 200 OK\r\n"
                    b"Content-Type: text/plain; charset=utf-8\r\n"
                    + f"Content-Length: {len(body)}\r\n".encode("utf-8")
                    + b"\r\n"
                    + body
                )
                # Envia a resposta inteira.
                conn.sendall(resp)
            else:
                # Resposta 404 simples para outras rotas.
                body = b"Rota nao encontrada"
                resp = (
                    b"HTTP/1.0 404 Not Found\r\n"
                    b"Content-Type: text/plain; charset=utf-8\r\n"
                    + f"Content-Length: {len(body)}\r\n".encode("utf-8")
                    + b"\r\n"
                    + body
                )
                conn.sendall(resp)
            # Ao sair do with, conn é fechado; volta para aceitar outra conexão.
