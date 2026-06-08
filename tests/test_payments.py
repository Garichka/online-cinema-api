from unittest.mock import MagicMock, patch


@patch("app.payments.services.stripe.checkout.Session.create")
def test_create_checkout(mock_stripe_create, client, auth_headers):
    mock_stripe_create.return_value = MagicMock(
        url="https://checkout.stripe.com/pay/test",
        id="cs_test_123",
        customer=None,
    )
    response = client.post(
        "/payments/checkout",
        json={
            "success_url": "http://test.com/success",
            "cancel_url": "http://test.com/cancel",
        },
        headers=auth_headers,
    )
    assert response.status_code == 201
    assert "checkout_url" in response.json()


def test_webhook_missing_signature(client):
    response = client.post("/payments/webhook", content=b"{}")
    assert response.status_code == 400


@patch("app.payments.router.stripe.Webhook.construct_event")
def test_webhook_success(mock_construct_event, client, user_in_db):
    mock_construct_event.return_value = {
        "type": "checkout.session.completed",
        "data": {
            "object": {
                "id": "cs_test_123",
                "customer": "cus_test_123",
                "metadata": {"user_id": str(user_in_db["id"])},
            }
        },
    }

    with patch("app.payments.router.send_premium_welcome_email"):
        response = client.post(
            "/payments/webhook",
            content=b"{}",
            headers={"Stripe-Signature": "test_sig"},
        )

    assert response.status_code == 200
    assert response.json() == {"status": "success"}
