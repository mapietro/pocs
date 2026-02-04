from pydantic import BaseModel

class LoginRequest(BaseModel):
    username: str
    password: str

class AuthMeResponse(BaseModel):
    username: str

class ChangePasswordRequest(BaseModel):
    current_password: str
    new_password: str

class OkResponse(BaseModel):
    ok: bool = True
