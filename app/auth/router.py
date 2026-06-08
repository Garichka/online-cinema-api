import jwt
from datetime import datetime, timezone
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload

from app.core.database import get_db
from app.auth.schemas import (
    UserCreate,
    UserResponse,
    UserLogin,
    TokenResponse,
    TokenRefreshRequest,
)
from app.auth.services import AuthService
from app.auth.models import ActivationToken, User, RefreshToken
from app.core.config import settings

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post(
    "/register",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
)
async def register(user_data: UserCreate, db: AsyncSession = Depends(get_db)):

    new_user = await AuthService.register_new_user(db, user_data)

    stmt = (
        select(User)
        .options(
            selectinload(User.group),
            selectinload(User.profile),
        )
        .where(User.id == new_user.id)
    )

    result = await db.execute(stmt)
    user = result.scalar_one()

    return user


@router.get("/activate", status_code=status.HTTP_200_OK)
async def activate_account(
    token: str = Query(...),
    db: AsyncSession = Depends(get_db),
):

    stmt = select(ActivationToken).where(ActivationToken.token == token)
    result = await db.execute(stmt)
    db_token = result.scalar_one_or_none()

    if not db_token:
        raise HTTPException(
            status_code=400, detail="Invalid or expired activation token."
        )

    if db_token.expires_at.replace(tzinfo=timezone.utc) < datetime.now(timezone.utc):
        await db.delete(db_token)
        await db.commit()
        raise HTTPException(status_code=400, detail="Token has expired.")

    user_stmt = select(User).where(User.id == db_token.user_id)
    user = (await db.execute(user_stmt)).scalar_one_or_none()

    if not user:
        raise HTTPException(status_code=404, detail="User not found.")

    user.is_active = True
    await db.delete(db_token)
    await db.commit()

    return {"status": "success", "message": "Account activated"}


@router.post("/login", response_model=TokenResponse)
async def login(user_data: UserLogin, db: AsyncSession = Depends(get_db)):
    user = await AuthService.authenticate_user(db, user_data)
    return await AuthService.create_user_tokens(db, user.id)


@router.post("/refresh", response_model=TokenResponse)
async def refresh_tokens(
    payload: TokenRefreshRequest,
    db: AsyncSession = Depends(get_db),
):

    token_data = jwt.decode(
        payload.refresh_token,
        settings.JWT_SECRET_KEY,
        algorithms=[settings.JWT_ALGORITHM],
    )

    if token_data.get("type") != "refresh":
        raise HTTPException(status_code=401, detail="Invalid token type.")

    user_id = int(token_data.get("sub"))

    stmt = select(RefreshToken).where(RefreshToken.token == payload.refresh_token)
    db_token = (await db.execute(stmt)).scalar_one_or_none()

    if not db_token:
        raise HTTPException(status_code=401, detail="Invalid refresh token.")

    await db.delete(db_token)
    await db.commit()

    return await AuthService.create_user_tokens(db, user_id)
