from fastapi import Depends, Request, Header, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.deps.db import get_session  # já existe no seu projeto (get_session)
from app.db.repositories.auth_repository import AuthRepository
from app.core.throttle import InMemoryLoginThrottle
from app.core.csrf import is_valid_csrf
from app.services.auth_service import AuthService, Unauthorized

_throttle_singleton = InMemoryLoginThrottle()

def get_auth_repository(db: AsyncSession = Depends(get_session)) -> AuthRepository:
    return AuthRepository(db)

def get_auth_service(
    repo: AuthRepository = Depends(get_auth_repository),
) -> AuthService:
    # no projeto real: ttl vem do settings
    return AuthService(repo=repo, throttle=_throttle_singleton, session_ttl_hours=12)

def require_csrf(
    request: Request,
    x_csrf_token: str | None = Header(default=None, alias="X-CSRF-Token"),
) -> None:
    cookie_token = request.cookies.get("csrf")
    if not is_valid_csrf(cookie_token, x_csrf_token):
        raise HTTPException(status_code=403, detail="CSRF invalid")

def get_session_token(request: Request) -> str | None:
    return request.cookies.get("ijazz_session")  # no real: nome via config

async def require_user(
    request: Request,
    service: AuthService = Depends(get_auth_service),
) -> str:
    token = get_session_token(request)
    if not token:
        raise HTTPException(status_code=401, detail="Not authenticated")
    try:
        # no real: retorna user (id/username)
        return await service.validate_session(token)
    except Unauthorized:
        raise HTTPException(status_code=401, detail="Not authenticated")
