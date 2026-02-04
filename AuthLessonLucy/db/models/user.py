from sqlalchemy import String, DateTime, Boolean
from sqlalchemy.orm import Mapped, mapped_column
from datetime import datetime
import secrets

from app.db.models.base import Base  # no seu projeto já existe Base comum

class User(Base):
    """
    CONCEITO: Identidade persistida.
    - Senha nunca é guardada.
    - Guardamos apenas password_hash.
    - auth_version_token é o "segredo" da revogação total:
      se ele muda, todas as sessões antigas morrem.
    """
    __tablename__ = "users"

    id: Mapped[str] = mapped_column(String, primary_key=True)  # ajuste para UUID se você usa
    username: Mapped[str] = mapped_column(String(120), unique=True, index=True, nullable=False)
    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)

    auth_version_token: Mapped[str] = mapped_column(
        String(64),
        nullable=False,
        default=lambda: secrets.token_urlsafe(16),
        index=True,
    )

    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
