import logging
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

from app.config import settings

logger = logging.getLogger(__name__)


def _send(to: str, subject: str, body: str) -> None:
    if not settings.smtp_user:
        logger.info("SMTP not configured — skipping email to %s: %s", to, subject)
        return

    msg = MIMEMultipart("alternative")
    msg["Subject"] = subject
    msg["From"] = settings.smtp_user
    msg["To"] = to
    msg.attach(MIMEText(body, "html"))

    try:
        with smtplib.SMTP(settings.smtp_host, settings.smtp_port) as server:
            server.starttls()
            server.login(settings.smtp_user, settings.smtp_password)
            server.sendmail(settings.smtp_user, to, msg.as_string())
    except Exception:
        logger.exception("Failed to send email to %s", to)


def send_booking_confirmation(
    guest_email: str,
    guest_name: str,
    schedule_name: str,
    slot_start: str,
    confirmation_link: str,
    cancel_link: str,
) -> None:
    body = f"""
    <p>Привет, {guest_name}!</p>
    <p>Вы записались на <strong>{schedule_name}</strong> ({slot_start}).</p>
    <p>Для подтверждения брони нажмите кнопку ниже:</p>
    <p><a href="{confirmation_link}" style="background:#6366f1;color:#fff;padding:10px 20px;border-radius:6px;text-decoration:none;">Подтвердить запись</a></p>
    <p>Чтобы отменить запись: <a href="{cancel_link}">отменить</a></p>
    """
    _send(guest_email, f"Подтвердите запись: {schedule_name}", body)


def send_booking_confirmed_to_host(
    host_email: str,
    host_name: str,
    guest_name: str,
    guest_email: str,
    schedule_name: str,
    slot_start: str,
) -> None:
    body = f"""
    <p>Привет, {host_name}!</p>
    <p><strong>{guest_name}</strong> ({guest_email}) подтвердил запись на <strong>{schedule_name}</strong> ({slot_start}).</p>
    """
    _send(host_email, f"Новая запись: {guest_name} — {schedule_name}", body)


def send_booking_cancelled(
    to_email: str,
    to_name: str,
    guest_name: str,
    schedule_name: str,
    slot_start: str,
) -> None:
    body = f"""
    <p>Привет, {to_name}!</p>
    <p>Запись <strong>{guest_name}</strong> на <strong>{schedule_name}</strong> ({slot_start}) была отменена.</p>
    """
    _send(to_email, f"Запись отменена: {schedule_name}", body)
