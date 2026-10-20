import logging

import resend

from app.core.config import settings

logger = logging.getLogger(__name__)


def send_welcome_email(to_email: str) -> None:
    """
    Sends a welcome email to the user who joined the waitlist.
    This function should be executed as a background task.
    """
    if not settings.resend_api_key:
        logger.warning("RESEND_API_KEY is not set. Skipping welcome email dispatch.")
        return

    resend.api_key = settings.resend_api_key
    resend.default_http_client = resend.RequestsClient(timeout=5)

    subject = "OSJ learning demo registration"
    html_content = """
    <div style="font-family: Arial, sans-serif; max-width: 600px; margin: auto;">
        <h2>Welcome to OSJ — Open Source Justify</h2>
        <p>This is an educational registration example configured by its operator.</p>
        <p>Bundled data is fictional. This demo does not provide real legal advice,
        verified Bangladesh-law answers, or access to a production legal service.</p>
    </div>
    """

    try:
        resend.Emails.send(
            {"from": settings.resend_from_email, "to": [to_email], "subject": subject, "html": html_content}
        )
        logger.info("Welcome email dispatched")
    except Exception:
        logger.error("Welcome email delivery failed")


class ResendWelcomeEmail:
    def send_welcome(self, email: str) -> None:
        send_welcome_email(to_email=email)
