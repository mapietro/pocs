from fastapi import APIRouter, Depends, Request, Response, HTTPException
from app.schemas.auth.api import LoginRequest, OkResponse, ChangePasswordRequest, AuthMeResponse
from app.deps.auth import get_auth_service, require_user, require_csrf
from app.core.csrf import new_csrf_token
from app.services.auth_service import InvalidCredentials, LockedOut

router = APIRouter(prefix="/auth", tags=["auth"])

@router.get("/csrf", response_model=OkResponse)
async def csrf(response: Response, request: Request) -> OkResponse:
    """
    CONCEITO: endpoint simples para o frontend obter/setar cookie CSRF.
    Double submit: cookie + header.
    """
    token = new_csrf_token()
    response.set_cookie(
        key="csrf",
        value=token,
        httponly=False,         # precisa ser legível pelo JS (para enviar no header)
        samesite="lax",
        secure=False,           # True em prod HTTPS
        path="/",
    )
    return OkResponse()

@router.post("/login", response_model=OkResponse)
async def login(payload: LoginRequest, request: Request, response: Response, service=Depends(get_auth_service)) -> OkResponse:
    try:
        ip = request.client.host if request.client else "unknown"
        raw_token = await service.login(payload.username, payload.password, ip=ip)

        response.set_cookie(
            key="ijazz_session",
            value=raw_token,
            httponly=True,
            samesite="lax",
            secure=False,  # True em prod
            path="/",
        )
        return OkResponse()
    except LockedOut:
        raise HTTPException(status_code=429, detail="Try again later")
    except InvalidCredentials:
        raise HTTPException(status_code=401, detail="Invalid credentials")

@router.get("/me", response_model=AuthMeResponse)
async def me(username=Depends(require_user)) -> AuthMeResponse:
    return AuthMeResponse(username=username)

@router.post("/logout", dependencies=[Depends(require_csrf)], response_model=OkResponse)
async def logout(request: Request, response: Response, service=Depends(get_auth_service)) -> OkResponse:
    token = request.cookies.get("ijazz_session")
    if token:
        await service.logout(token)
    response.delete_cookie("ijazz_session", path="/")
    return OkResponse()

@router.post("/change-password", dependencies=[Depends(require_csrf)], response_model=OkResponse)
async def change_password(
    payload: ChangePasswordRequest,
    username=Depends(require_user),
    service=Depends(get_auth_service),
) -> OkResponse:
    await service.change_password(username, payload.current_password, payload.new_password)
    return OkResponse()
