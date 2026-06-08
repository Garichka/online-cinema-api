from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.auth.dependencies import get_current_user
from app.auth.models import User
from app.payments.schemas import (
    CheckoutSessionCreate,
    CheckoutSessionResponse,
)
from app.payments.services import PaymentService

router = APIRouter(
    prefix="/payments",
    tags=["Payments & Subscriptions"],
)


@router.post(
    "/checkout",
    response_model=CheckoutSessionResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a premium subscription checkout session",
)
async def create_checkout_session(
    data: CheckoutSessionCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return await PaymentService.create_subscription_session(
        db=db,
        user_id=current_user.id,
        data=data,
    )
