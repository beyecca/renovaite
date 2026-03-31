import smtplib
from email.message import EmailMessage

from renovaite.settings.base import Settings, get_settings


def send_magic_link_email(
    email: str, token: str, settings: Settings | None = None
) -> None:
    if settings is None:
        settings = get_settings()

    verify_url = f"{settings.magic_link_base_url}/auth/verify?token={token}"

    msg = EmailMessage()
    msg["Subject"] = "Your Renovaite login link"
    msg["From"] = settings.mail_from
    msg["To"] = email
    msg.set_content(
        f"Click the link below to log in to Renovaite. "
        f"This link expires in {settings.magic_link_expiry_minutes} minutes.\n\n"
        f"{verify_url}\n"
    )

    if settings.mail_console:
        print(f"[EMAIL] To: {email}\nSubject: {msg['Subject']}\n{verify_url}")
        return

    with smtplib.SMTP(settings.mail_server, settings.mail_port) as smtp:
        if settings.mail_use_tls:
            smtp.starttls()
        if settings.mail_username:
            smtp.login(settings.mail_username, settings.mail_password)
        smtp.send_message(msg)
