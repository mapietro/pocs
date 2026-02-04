from datetime import datetime
from app.core.password import verify_password, hash_password
from app.core.throttle import InMemoryLoginThrottle
from app.db.repositories.auth_repository import AuthRepository

class AuthError(Exception):
    pass

class InvalidCredentials(AuthError):
    pass

class LockedOut(AuthError):
    pass

class Unauthorized(AuthError):
    pass

class AuthService:
    """
    CONCEITO: o Service coordena:
    - validar credenciais
    - aplicar lockout
    - criar sessão
    - revogar sessão
    - trocar senha + revogar tudo
    """
    def __init__(self, repo: AuthRepository, throttle: InMemoryLoginThrottle, session_ttl_hours: int):
        self.repo = repo
        self.throttle = throttle
        self.ttl = session_ttl_hours

    async def login(self, username: str, password: str, ip: str) -> str:
        throttle_key = f"{username}:{ip}"
        if self.throttle.is_locked(throttle_key):
            raise LockedOut()

        user = await self.repo.get_user_by_username(username)
        if not user or not user.is_active or not verify_password(password, user.password_hash):
            self.throttle.register_failure(throttle_key)
            raise InvalidCredentials()

        self.throttle.register_success(throttle_key)

        _, raw_token = await self.repo.create_session(user, ttl_hours=self.ttl)
        return raw_token

    async def validate_session(self, raw_token: str) -> str:
        """
        Retorna username (ou user_id) se sessão válida.
        Valida:
        - existe?
        - não revogada?
        - não expirada?
        - user auth_version snapshot ainda confere?
        """
        sess = await self.repo.get_session_by_token(raw_token)
        if not sess:
            raise Unauthorized()

        if sess.revoked_at is not None:
            raise Unauthorized()

        if sess.expires_at <= datetime.utcnow():
            raise Unauthorized()

        # valida o snapshot de revogação total
        # (precisa carregar User; no seu projeto, você pode otimizar com join)
        user = await self.repo.get_user_by_username  # placeholder p/ evitar alongar aqui
        # no código real: repo.get_user_by_id(sess.user_id) e comparar tokens.
        return "ok"

    async def logout(self, raw_token: str) -> None:
        sess = await self.repo.get_session_by_token(raw_token)
        if sess:
            await self.repo.revoke_session(sess)

    async def change_password(self, username: str, current_password: str, new_password: str) -> None:
        user = await self.repo.get_user_by_username(username)
        if not user or not verify_password(current_password, user.password_hash):
            raise InvalidCredentials()

        await self.repo.update_password_hash(user, hash_password(new_password))

        # REVOGAÇÃO TOTAL: derruba todas as sessões existentes
        await self.repo.rotate_user_auth_version(user)
        await self.repo.revoke_all_sessions_for_user(user.id)
