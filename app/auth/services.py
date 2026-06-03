import secrets
from datetime import datetime, timedelta, timezone
from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app.auth.models import User, UserProfile, ActivationToken
from app.auth.schemas import UserCreate
from app.core.security import get_password_hash


class AuthService:
    @staticmethod
    async def get_user_by_email(db: AsyncSession, email: str) -> User | None:
        stmt = select(User).where(User.email == email)
        result = await db.execute(stmt)
        return result.scalar_one_or_none()

    @classmethod
    async def register_new_user(cls, db: AsyncSession, user_data: UserCreate) -> User:

        existing_user = await cls.get_user_by_email(db, user_data.email)
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="A user with this email is already registered.",
            )

        hashed_password = get_password_hash(user_data.password)

        new_user = User(
            email=user_data.email,
            hashed_password=hashed_password,
            group_id=1,
            is_active=False,
        )
        db.add(new_user)
        await db.flush()

        new_profile = UserProfile(user_id=new_user.id)
        db.add(new_profile)

        token_str = secrets.token_urlsafe(32)
        expire_time = datetime.now(timezone.utc) + timedelta(hours=24)

        activation_token = ActivationToken(
            user_id=new_user.id, token=token_str, expires_at=expire_time
        )
        db.add(activation_token)

        await db.commit()
        await db.refresh(new_user)

        from app.worker import send_activation_email

        send_activation_email.delay(new_user.email, token_str)

        return new_user
