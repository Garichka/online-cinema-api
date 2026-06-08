import stripe
from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.payments.models import Payment
from app.payments.schemas import (
    CheckoutSessionCreate,
    CheckoutSessionResponse,
)

stripe.api_key = settings.STRIPE_SECRET_KEY


class PaymentService:
    @staticmethod
    async def create_subscription_session(
        db: AsyncSession,
        user_id: int,
        data: CheckoutSessionCreate,
    ) -> CheckoutSessionResponse:
        try:
            session = stripe.checkout.Session.create(
                payment_method_types=["card"],
                line_items=[
                    {
                        "price_data": {
                            "currency": "usd",
                            "product_data": {
                                "name": "Cinema API Premium Subscription",
                                "description": (
                                    "Unlimited access to all movies, "
                                    "4K quality, and an ad-free experience."
                                ),
                            },
                            "unit_amount": 999,
                            "recurring": {
                                "interval": "month",
                            },
                        },
                        "quantity": 1,
                    }
                ],
                mode="subscription",
                success_url=data.success_url,
                cancel_url=data.cancel_url,
                metadata={
                    "user_id": str(user_id),
                },
            )

            new_payment = Payment(
                user_id=user_id,
                stripe_checkout_session_id=session.id,
                stripe_customer_id=session.customer,
                amount=9.99,
                currency="usd",
                status="pending",
            )

            db.add(new_payment)
            await db.commit()

            return CheckoutSessionResponse(
                checkout_url=session.url,
                session_id=session.id,
            )

        except stripe.error.StripeError as e:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Stripe payment gateway error: {str(e)}",
            )

        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Internal error while creating payment: {str(e)}",
            )
