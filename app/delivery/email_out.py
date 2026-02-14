"""Email delivery via SMTP."""

import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

from config import settings


class EmailDelivery:
    def deliver(self, recap: str, subject: str = "Hotel Intel — Daily Recap", **kwargs) -> None:
        if not settings.SMTP_USER or not settings.EMAIL_TO:
            raise RuntimeError("Email not configured. Set SMTP_USER, SMTP_PASSWORD, EMAIL_TO in .env")

        msg = MIMEMultipart("alternative")
        msg["From"] = settings.EMAIL_FROM or settings.SMTP_USER
        msg["To"] = settings.EMAIL_TO
        msg["Subject"] = subject

        # Send as plain text (Markdown)
        msg.attach(MIMEText(recap, "plain", "utf-8"))

        with smtplib.SMTP(settings.SMTP_HOST, settings.SMTP_PORT) as server:
            server.starttls()
            server.login(settings.SMTP_USER, settings.SMTP_PASSWORD)
            server.send_message(msg)

        print(f"✅ Recap emailed to {settings.EMAIL_TO}")
