import smtplib
import logging
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from app.core.config import settings

logger = logging.getLogger(__name__)


def send_status_update_email(to_email: str, complaint_title: str, new_status: str, department: str) -> None:
    """Dispatches a status update notification email in the background."""
    if not settings.SMTP_USER or not settings.SMTP_PASSWORD:
        logger.info(
            f"[MOCK EMAIL] To: {to_email} | Ticket '{complaint_title}' updated to '{new_status}' ({department})"
        )
        return

    subject = f"[Smart Campus] Update on Ticket: {complaint_title}"
    body = f"""
    Hello,

    Your campus maintenance ticket has been updated:

    - Title: {complaint_title}
    - Status: {new_status}
    - Assigned Department: {department}

    You can track live progress directly from your student dashboard.

    Best regards,
    {settings.EMAILS_FROM_NAME}
    """

    msg = MIMEMultipart()
    msg["From"] = f"{settings.EMAILS_FROM_NAME} <{settings.EMAILS_FROM_EMAIL}>"
    msg["To"] = to_email
    msg["Subject"] = subject
    msg.attach(MIMEText(body, "plain"))

    try:
        with smtplib.SMTP(settings.SMTP_HOST, settings.SMTP_PORT) as server:
            server.starttls()
            server.login(settings.SMTP_USER, settings.SMTP_PASSWORD)
            server.sendmail(settings.EMAILS_FROM_EMAIL, to_email, msg.as_string())
            logger.info(f"Notification email dispatched to {to_email}")
    except Exception as e:
        logger.error(f"Failed to send email to {to_email}: {e}")