# utils/emailer.py

import smtplib
from email.message import EmailMessage
import streamlit as st

def send_email(to_email: str, subject: str, body: str):
    """
    Send a plain-text email via SMTP using credentials stored in Streamlit secrets.
    """
    smtp_user = st.secrets["DEFAULT_EMAIL"]
    smtp_pass = st.secrets["EMAIL_PASSWORD"]

    msg = EmailMessage()
    msg["Subject"] = subject
    msg["From"] = smtp_user
    msg["To"] = to_email
    msg.set_content(body)

    try:
        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as smtp:
            smtp.login(smtp_user, smtp_pass)
            smtp.send_message(msg)
            print(f"✅ Email sent to {to_email}")
    except Exception as e:
        print(f"❌ Failed to send email to {to_email}: {e}")

def send_registration_email(email: str, token: str):
    """
    Email the user a registration confirmation link with embedded token.
    """
    link = f"https://youtufy-one.streamlit.app/pages/verify_token.py?token={token}"
    subject = "Confirm Your YouTufy Registration"
    body = f"""
    Welcome to YouTufy 🎉

    Please verify your email address to activate your account:

    {link}

    If you didn't register, you can ignore this message.

    – The YouTufy Team
    """
    send_email(email, subject, body)

def send_password_reset_email(email: str, token: str):
    """
    Send password reset instructions with tokenized link.
    """
    link = f"https://youtufy-one.streamlit.app/pages/update_password.py?token={token}"
    subject = "Reset Your YouTufy Password"
    body = f"""
    Hello,

    A password reset was requested for your YouTufy account.

    Please click the link below to reset your password:

    {link}

    This link will expire in 1 hour.

    If you didn't request a reset, you can ignore this email.

    – The YouTufy Team
    """
    send_email(email, subject, body)
