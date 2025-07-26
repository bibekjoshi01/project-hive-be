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


def insert_user_account_verification(user_id: int, otp: str, conn=None):
    now = datetime.now()
    query = f"""
    INSERT INTO user_verification (
        user_id, otp, created_at
    )
    VALUES (
        {user_id}, '{otp}', '{now.isoformat()}'
    );
    """
    execute_query(query=query, conn=conn)


def send_otp_email(recipient_email: str, user_id: int, conn=None):
    subject = "Your OTP Code"
    sender_email = EMAIL_USERNAME
    otp = str(random.randint(100000, 999999))

    insert_user_account_verification(user_id, otp, conn)
    message = MIMEMultipart("alternative")
    message["Subject"] = subject
    message["From"] = sender_email
    message["To"] = recipient_email

    text = f"Your OTP code is: {otp}"

    html = f"""
    <html>
    <body style="font-family: Arial, sans-serif; background-color: #f4f4f4; margin: 0; padding: 0;">
        <table align="center" border="0" cellpadding="0" cellspacing="0" width="100%" style="padding: 20px 0;">
            <tr>
                <td align="center">
                    <table border="0" cellpadding="0" cellspacing="0" width="600" style="background-color: #ffffff; border-radius: 8px; padding: 20px;">
                        <tr>
                            <td align="center" style="padding-bottom: 20px;">
                                <h2 style="color: #333333; margin: 0;">Thapathali Project Archive</h2>
                            </td>
                        </tr>
                        <tr>
                            <td style="padding: 20px; text-align: center; color: #555555; font-size: 16px;">
                                <p style="margin: 0 0 10px;">Hello,</p>
                                <p style="margin: 0 0 20px;">Your OTP code is:</p>
                                <p style="font-size: 24px; font-weight: bold; color: #ffffff; background-color: #4CAF50; padding: 10px 20px; border-radius: 4px; display: inline-block;">
                                    {otp}
                                </p>
                                <p style="margin: 20px 0 0;">This code will expire in <strong>10 minutes</strong>.</p>
                            </td>
                        </tr>
                        <tr>
                            <td style="padding: 20px; text-align: center; color: #aaaaaa; font-size: 12px;">
                                <p style="margin: 0;">If you didn’t request this, you can ignore this email.</p>
                            </td>
                        </tr>
                    </table>
                </td>
            </tr>
        </table>
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
