import secrets
import hmac

CSRF_COOKIE_NAME = "csrf"  # no projeto real: prefixe (ex: ops_csrf)

def new_csrf_token() -> str:
    # CONCEITO: token aleatório por sessão (ou por request).
    return secrets.token_hex(16)

def is_valid_csrf(cookie_token: str | None, header_token: str | None) -> bool:
    # CONCEITO: Double Submit => o browser envia 2 cópias do mesmo segredo:
    # - uma no cookie
    # - outra num header explícito (prova intenção)
    if not cookie_token or not header_token:
        return False
    return hmac.compare_digest(cookie_token, header_token)
