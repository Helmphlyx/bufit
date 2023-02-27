from typing import List

from itsdangerous import URLSafeTimedSerializer
from flask_mail import Message

from application import application, mail

ts = URLSafeTimedSerializer(application.config["SECRET_KEY"])


def send_email(recipients: List[str], subject: str, message: str):
    """Send email using flask-mail."""
    with application.app_context():
        msg = Message(
            subject=subject,
            sender=application.config.get("MAIL_USERNAME"),
            recipients=recipients,
            body=message,
        )
        mail.send(msg)
