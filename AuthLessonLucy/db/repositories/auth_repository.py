from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update
from datetime import datetime

from app.db.models.user import User
from app.db.models.session import Session

class AuthRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_user_by_username(self, username: str) -> User | None:
        q = await self.db.execute(select(User).where(User.username == username))
        return q.scalar_one_or_none()

    async def create_session(self, user: User, ttl_hours: int) -> tuple[Session, str]:
        raw_token = Session.new_token()
        token_hash = Session.hash_token(raw_token)
        session = Session(
            id=raw_token[:20],  # ajuste; ideal: uuid
            user_id=user.id,
            session_token_hash=token_hash,
            user_auth_version_snapshot=user.auth_version_token,
            expires_at=Session.compute_expires(ttl_hours),
        )
        self.db.add(session)
        return session, raw_token

    async def get_session_by_token(self, raw_token: str) -> Session | None:
        token_hash = Session.hash_token(raw_token)
        q = await self.db.execute(
            select(Session).where(Session.session_token_hash == token_hash)
        )
        return q.scalar_one_or_none()

    async def revoke_session(self, session: Session) -> None:
        session.revoked_at = datetime.utcnow()
        self.db.add(session)

    async def revoke_all_sessions_for_user(self, user_id: str) -> None:
        await self.db.execute(
            update(Session)
            .where(Session.user_id == user_id, Session.revoked_at.is_(None))
            .values(revoked_at=datetime.utcnow())
        )

    async def rotate_user_auth_version(self, user: User) -> None:
        # CONCEITO: revogação total por “versão” do usuário.
        import secrets
        user.auth_version_token = secrets.token_urlsafe(16)
        self.db.add(user)

    async def update_password_hash(self, user: User, new_hash: str) -> None:
        user.password_hash = new_hash
        self.db.add(user)
