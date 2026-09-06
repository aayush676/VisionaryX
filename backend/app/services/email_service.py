"""Minimal email dispatch layer.

Defaults to a 'console' backend (prints to stdout) so signup/verification/reset
flows work end-to-end without SMTP credentials. Swap EMAIL_BACKEND=smtp and
fill in the SMTP_* settings in .env to send real emails via smtplib.
"""
import smtplib
from email.mime.text import MIMEText

from app.core.config import get_settings

settings = get_settings()


def _send_console(to_email: str, subject: str, body: str) -> None:
    print(f"\n----- [EMAIL:{settings.email_backend}] -----")
    print(f"To: {to_email}\nSubject: {subject}\n\n{body}")
    print("----------------------------------\n")


def _send_smtp(to_email: str, subject: str, body: str) -> None:
    message = MIMEText(body)
    message["Subject"] = subject
    message["From"] = settings.email_from
    message["To"] = to_email

    with smtplib.SMTP(settings.smtp_host, settings.smtp_port) as server:
        server.starttls()
        if settings.smtp_user:
            server.login(settings.smtp_user, settings.smtp_password)
        server.sendmail(settings.email_from, [to_email], message.as_string())


def send_email(to_email: str, subject: str, body: str) -> None:
    if settings.email_backend == "smtp" and settings.smtp_host:
        _send_smtp(to_email, subject, body)
    else:
        _send_console(to_email, subject, body)


def send_verification_email(to_email: str, token: str) -> None:
    link = f"{settings.frontend_origin}/verify-email?token={token}"
    send_email(to_email, "Verify your VisionaryX account", f"Click to verify your account:\n{link}")


def send_password_reset_email(to_email: str, token: str) -> None:
    link = f"{settings.frontend_origin}/reset-password?token={token}"
    send_email(to_email, "Reset your VisionaryX password", f"Click to reset your password:\n{link}")
