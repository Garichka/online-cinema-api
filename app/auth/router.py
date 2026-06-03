from datetime import datetime, timezone
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload

from app.core.database import get_db
from app.auth.schemas import UserCreate, UserResponse
from app.auth.services import AuthService
from app.auth.models import ActivationToken, User

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post(
    "/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED
)
async def register(user_data: UserCreate, db: AsyncSession = Depends(get_db)):
    new_user = await AuthService.register_new_user(db, user_data)

    stmt = select(User).options(selectinload(User.group)).where(User.id == new_user.id)
    result = await db.execute(stmt)
    return result.scalar_one()


@router.get("/activate", status_code=status.HTTP_200_OK)
async def activate_account(
    token: str = Query(..., description="Activation token from email"),
    db: AsyncSession = Depends(get_db),
):

    stmt = select(ActivationToken).where(ActivationToken.token == token)
    result = await db.execute(stmt)
    db_token = result.scalar_one_or_none()

    if not db_token:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid or expired activation token.",
        )

    if db_token.expires_at.replace(tzinfo=timezone.utc) < datetime.now(timezone.utc):
        await db.delete(db_token)
        await db.commit()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Token has expired. Please register again.",
        )

    user_stmt = select(User).where(User.id == db_token.user_id)
    user_result = await db.execute(user_stmt)
    user = user_result.scalar_one_or_none()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User not found."
        )

    user.is_active = True

    await db.delete(db_token)
    await db.commit()

    return {
        "status": "success",
        "message": "Account successfully activated! You can now log in.",
    }
