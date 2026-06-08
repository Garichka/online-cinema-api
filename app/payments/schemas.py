from pydantic import BaseModel, Field


class CheckoutSessionCreate(BaseModel):
    success_url: str = Field(
        description="URL to redirect the user to after a successful payment",
    )

    cancel_url: str = Field(
        description="URL to redirect the user to if the payment is canceled or fails",
    )


class CheckoutSessionResponse(BaseModel):
    checkout_url: str
    session_id: str
