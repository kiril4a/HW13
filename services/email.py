# services/email.py

from pathlib import Path
from fastapi_mail import FastMail, MessageSchema, ConnectionConfig, MessageType
from pydantic import EmailStr
from repository.users import confirmed_email
from config import Settings
TEMPLATE_FOLDER = Path(__file__).parent / 'templates'

settings = Settings()

conf = ConnectionConfig(
    MAIL_USERNAME=settings.MAIL_USERNAME,
    MAIL_PASSWORD=settings.MAIL_PASSWORD,
    MAIL_FROM=settings.MAIL_FROM,
    MAIL_PORT=settings.MAIL_PORT,
    MAIL_SERVER=settings.MAIL_SERVER,
    MAIL_FROM_NAME=settings.MAIL_FROM_NAME,
    MAIL_STARTTLS=settings.MAIL_STARTTLS,
    MAIL_SSL_TLS=settings.MAIL_SSL_TLS,
    USE_CREDENTIALS=settings.USE_CREDENTIALS,
    VALIDATE_CERTS=settings.VALIDATE_CERTS,
    TEMPLATE_FOLDER=TEMPLATE_FOLDER
)

async def send_email(email: EmailStr, username: str, confirmation_url: str):
    try:
        message = MessageSchema(
            subject="Confirm your email",
            recipients=[email],
            template_body={"username": username, "confirmation_url": confirmation_url},
            subtype=MessageType.html
        )

        fm = FastMail(conf)
        await fm.send_message(message, template_name="email_template.html")
    except Exception as e:
        print(f"An error occurred while sending email: {e}")
