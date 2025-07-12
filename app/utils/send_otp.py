from datetime import datetime
import ssl
import random
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from app.config import settings
from app.database import execute_query

EMAIL_HOST = settings.email_host
EMAIL_PORT = settings.email_port
EMAIL_USERNAME = settings.email_username
EMAIL_PASSWORD = settings.email_password


def insert_user_account_verification(user_id: int, otp: str):
    now = datetime.now()
    query = f"""
    INSERT INTO user_verification (
        user_id, otp, created_at
    )
    VALUES (
        {user_id}, '{otp}', '{now.isoformat()}'
    );
    """
    execute_query(query)


def send_otp_email(recipient_email: str, user_id: int):
    subject = "Your OTP Code"
    sender_email = EMAIL_USERNAME
    otp = str(random.randint(100000, 999999))

    insert_user_account_verification(user_id, otp)
    message = MIMEMultipart("alternative")
    message["Subject"] = subject
    message["From"] = sender_email
    message["To"] = recipient_email

    text = f"Your OTP code is: {otp}"
    html = f"""
    <html>
        <body>
            <p>Hi,<br>
            Your OTP code is: <b>{otp}</b><br>
            It will expire in 10 minutes.
            </p>
        </body>
    </html>
    """

    part1 = MIMEText(text, "plain")
    part2 = MIMEText(html, "html")

    message.attach(part1)
    message.attach(part2)

    context = ssl.create_default_context()
    with smtplib.SMTP(EMAIL_HOST, EMAIL_PORT) as server:
        server.starttls(context=context)
        server.login(sender_email, EMAIL_PASSWORD)
        server.sendmail(sender_email, recipient_email, message.as_string())
