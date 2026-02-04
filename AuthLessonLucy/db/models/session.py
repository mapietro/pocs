from sqlalchemy import String, DateTime, ForeignKey, Index
from sqlalchemy.orm import Mapped, mapped_column
from datetime import datetime, timedelta
import secrets, hashlib

from app.db.models.base import Base

class Session(Base):
    """
    CONCEITO: Sessão stateful.
    - O browser guarda um cookie com um token (opaco).
    - O servidor guarda o HASH do token (se o DB vazar, tokens não vazam).
    - revogação/expiração é controlada pelo servidor.
    """
    __tablename__ = "sessions"

    id: Mapped[str] = mapped_column(String, primary_key=True)
    user_id: Mapped[str] = mapped_column(String, ForeignKey("users.id"), index=True, nullable=False)

    session_token_hash: Mapped[str] = mapped_column(String(64), unique=True, index=True, nullable=False)

    # Guarda o auth_version_token do usuário no momento do login.
    # Se o usuário trocar senha e esse token mudar, sessões antigas caem.
    user_auth_version_snapshot: Mapped[str] = mapped_column(String(64), nullable=False)

    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)
    expires_at: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    revoked_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)

    @staticmethod
    def new_token() -> str:
        return secrets.token_urlsafe(32)

    @staticmethod
    def hash_token(token: str) -> str:
        return hashlib.sha256(token.encode("utf-8")).hexdigest()

    @staticmethod
    def compute_expires(ttl_hours: int) -> datetime:
        return datetime.utcnow() + timedelta(hours=ttl_hours)

Index("ix_sessions_valid_lookup", Session.session_token_hash, Session.revoked_at, Session.expires_at)
