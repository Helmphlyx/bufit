from typing import List

from itsdangerous import URLSafeTimedSerializer
from flask_mail import Message

from app import app, mail

ts = URLSafeTimedSerializer(app.config["SECRET_KEY"])


def send_email(recipients: List[str], subject: str, message: str):
    """Send email using flask-mail."""
    with app.app_context():
        msg = Message(
            subject=subject,
            sender=app.config.get("MAIL_USERNAME"),
            recipients=recipients,
            body=message,
        )
        mail.send(msg)
