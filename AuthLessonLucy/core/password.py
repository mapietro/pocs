from passlib.context import CryptContext

_pwd = CryptContext(schemes=["argon2"], deprecated="auto")

def hash_password(raw: str) -> str:
    # CONCEITO: nunca guarde senha em logs. nunca retorne senha.
    return _pwd.hash(raw)

def verify_password(raw: str, password_hash: str) -> bool:
    return _pwd.verify(raw, password_hash)
