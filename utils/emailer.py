import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from dotenv import load_dotenv

load_dotenv()

# Base configuration
SENDER_EMAIL = os.getenv("DEFAULT_EMAIL")
SENDER_PASSWORD = os.getenv("EMAIL_PASSWORD")
BASE_URL = os.getenv("APP_URL", "https://youtufy-one.streamlit.app")

# -------------------------------
def send_registration_email(email, username, token):
    verification_link = f"{BASE_URL}/_verify_token?token={token}"

    message = MIMEMultipart("alternative")
    message["Subject"] = f"✅ Welcome to YouTufy, {username}! Verify your account"
    message["From"] = SENDER_EMAIL
    message["To"] = email

    text = f"""
Hi {username},

Thanks for signing up for YouTufy – your YouTube Subscriptions Dashboard.

Please verify your email address by clicking this link:
{verification_link}

If the link doesn't work, copy and paste it into your browser.

Thanks,
The YouTufy Team
"""
    html = f"""
<html>
  <body style="font-family: Arial, sans-serif; line-height: 1.6;">
    <h2>👋 Welcome to <span style="color:#ff00ff;">YouTufy</span>, {username}!</h2>
    <p>You're almost done – please verify your email to activate your dashboard.</p>
    <p style="text-align: center; margin: 30px 0;">
      <a href="{verification_link}" target="_blank" style="
          background-color: #ff00ff;
          color: white;
          padding: 14px 24px;
          border-radius: 6px;
          text-decoration: none;
          font-weight: bold;
          display: inline-block;
        ">✅ Verify My Account</a>
    </p>
    <p>If the button doesn't work, copy and paste this URL in your browser:</p>
    <p><a href="{verification_link}">{verification_link}</a></p>
    <p style="font-size: 14px; color: #555;">– The YouTufy Team</p>
  </body>
</html>
"""
    message.attach(MIMEText(text, "plain"))
    message.attach(MIMEText(html, "html"))

    try:
        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
            server.login(SENDER_EMAIL, SENDER_PASSWORD)
            server.sendmail(SENDER_EMAIL, email, message.as_string())
        print("✅ Verification email sent.")
    except Exception as e:
        print(f"❌ Failed to send verification email: {e}")

# -------------------------------
def send_password_reset_email(email, token):
    reset_url = f"{BASE_URL}/reset_password?token={token}"

    message = MIMEMultipart("alternative")
    message["Subject"] = "🔑 Reset your YouTufy password"
    message["From"] = SENDER_EMAIL
    message["To"] = email

    text = f"""
Hi,

We received a request to reset your YouTufy password.

Reset here:
{reset_url}

If you didn't request this, you can ignore this message.

– The YouTufy Team
"""
    html = f"""
<html>
  <body style="font-family: Arial, sans-serif;">
    <h3>Reset your password – YouTufy</h3>
    <p>We received a request to reset your password.</p>
    <p><a href="{reset_url}" target="_blank" style="padding: 10px 18px; background-color: #8F00FF; color: white; text-decoration: none; border-radius: 6px;">🔐 Reset Password</a></p>
    <p>If that doesn't work, click or paste this link:<br><a href="{reset_url}">{reset_url}</a></p>
    <p style="font-size: 14px; color: #888;">– The YouTufy Team</p>
  </body>
</html>
"""
    message.attach(MIMEText(text, "plain"))
    message.attach(MIMEText(html, "html"))

    try:
        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
            server.login(SENDER_EMAIL, SENDER_PASSWORD)
            server.sendmail(SENDER_EMAIL, email, message.as_string())
        print("✅ Password reset email sent.")
    except Exception as e:
        print(f"❌ Failed to send reset email: {e}")
