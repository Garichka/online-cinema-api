from unittest.mock import patch


@patch("app.payments.router.stripe.Webhook.construct_event")
@patch("app.payments.router.send_premium_welcome_email")
def test_email_task_called_on_successful_payment(
    mock_email_task, mock_construct_event, client, user_in_db
):

    mock_construct_event.return_value = {
        "type": "checkout.session.completed",
        "data": {
            "object": {
                "id": "cs_test_456",
                "customer": "cus_test_456",
                "metadata": {"user_id": str(user_in_db["id"])},
            }
        },
    }

    client.post(
        "/payments/webhook",
        content=b"{}",
        headers={"Stripe-Signature": "test_sig"},
    )

    mock_email_task.delay.assert_called_once_with(user_in_db["email"])
