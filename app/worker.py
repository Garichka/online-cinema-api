import time
import logging
from celery import Celery
from app.core.config import settings

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

celery_app = Celery(
    "cinema_worker",
    broker=settings.CELERY_BROKER_URL,
    backend=settings.CELERY_RESULT_BACKEND,
)

celery_app.conf.update(
    timezone="UTC",
    task_track_started=True,
    task_serializer="json",
    result_serializer="json",
    accept_content=["json"],
)


@celery_app.task(name="send_activation_email")
def send_activation_email(email: str, token: str) -> str:

    logger.info(f"Sending email request for: {email}")

    time.sleep(3)

    activation_link = (
        f"http://127.0.0.1:8000{settings.API_V1_STR}/auth/activate?token={token}"
    )

    logger.info("=========================================================")
    logger.info(f"EMAIL SUCCESSFULLY SENT TO: {email}")
    logger.info(f"Activation link: {activation_link}")
    logger.info("=========================================================")

    return f"Email sent to {email}"
