import stripe
from fastapi import APIRouter, Depends, status, Request, Header, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.auth.dependencies import get_current_user
from app.auth.models import User
from app.payments.schemas import (
    CheckoutSessionCreate,
    CheckoutSessionResponse,
)
from app.payments.services import PaymentService
from app.core.config import settings
from app.payments.models import Payment
from app.tasks.email_tasks import send_premium_welcome_email

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


@router.post(
    "/webhook",
    status_code=status.HTTP_200_OK,
    summary="Handle Stripe webhook events",
)
async def stripe_webhook(
    request: Request,
    stripe_signature: str = Header(
        None,
        alias="Stripe-Signature",
    ),
    db: AsyncSession = Depends(get_db),
):

    if not stripe_signature:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Missing Stripe signature header.",
        )

    payload = await request.body()

    try:
        event = stripe.Webhook.construct_event(
            payload,
            stripe_signature,
            settings.STRIPE_WEBHOOK_SECRET,
        )

    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid payload format.",
        )

    except stripe.error.SignatureVerificationError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Stripe signature verification failed.",
        )

    if event["type"] == "checkout.session.completed":
        session = event["data"]["object"]

        session_id = session.get("id")

        metadata = session.get("metadata", {})
        user_id_str = metadata.get("user_id")

        if user_id_str:
            user_id = int(user_id_str)

            payment_stmt = select(Payment).where(
                Payment.stripe_checkout_session_id == session_id
            )
            payment_res = await db.execute(payment_stmt)
            payment = payment_res.scalar_one_or_none()

            if payment:
                payment.status = "paid"
                payment.stripe_customer_id = session.get("customer")

            user_stmt = select(User).where(User.id == user_id)
            user_res = await db.execute(user_stmt)
            user = user_res.scalar_one_or_none()

            if user:
                user.is_premium = True
                send_premium_welcome_email.delay(user.email)
            await db.commit()

            print("=" * 57)
            print(
                f"🎉 SUBSCRIPTION ACTIVATED: User ID {user_id} "
                f"has been granted Premium access!"
            )
            print("=" * 57)

    return {"status": "success"}
