import os
import requests
from dotenv import load_dotenv

load_dotenv()  # Load from .env

MAILGUN_API_KEY = os.getenv("MAILGUN_API_KEY")
MAILGUN_DOMAIN = os.getenv("MAILGUN_DOMAIN")
FROM_EMAIL = os.getenv("DEFAULT_FROM_EMAIL")

def send_mailgun_email(to_email, subject, message):
    return requests.post(
        f"https://api.mailgun.net/v3/{MAILGUN_DOMAIN}/messages",
        auth=("api", MAILGUN_API_KEY),
        data={
            "from": FROM_EMAIL,
            "to": [to_email],
            "subject": subject,
            "text": message,
        }
    )
