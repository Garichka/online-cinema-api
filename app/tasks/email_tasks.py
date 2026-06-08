import time

from app.core.celery_app import celery_app


@celery_app.task(name="send_premium_welcome_email")
def send_premium_welcome_email(user_email: str):
    """
    Background task that simulates sending a premium welcome email
    after subscription activation.
    """
    print(f"📬 [Celery] Starting premium email send for {user_email}...")

    # Simulate network delay (e.g., Mailgun, SMTP, etc.)
    time.sleep(4)

    print(f"✅ [Celery] Email successfully sent to: {user_email}!")

    return f"Email sent to {user_email}"
