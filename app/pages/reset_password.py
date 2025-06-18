# app/pages/reset_password.py
import sys
import os
import sqlite3
import streamlit as st
from dotenv import load_dotenv

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

from utils.tokens import generate_token
from utils.emailer import send_password_reset_email

# 🔧 Environment Setup
load_dotenv()
DB_PATH = st.secrets["USER_DB"]

# 🎨 Page Setup
st.set_page_config(page_title="Reset Password – YouTufy", layout="centered")
st.title("🔑 Reset Your YouTufy Password")
st.markdown("Enter your registered email to receive a password reset link.")

# 🔁 Check if user exists
def user_exists(email: str) -> bool:
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("SELECT 1 FROM users WHERE email = ?", (email,))
    found = cur.fetchone() is not None
    conn.close()
    return found

# 📩 Password Reset Form
with st.form("reset_form"):
    email = st.text_input("📧 Registered Email")
    submitted = st.form_submit_button("Send Reset Link")

if submitted:
    if not email:
        st.error("❗ Email is required.")
    elif not user_exists(email):
        st.warning("⚠️ No account found with that email.")
    else:
        try:
            token = generate_token(email)
            send_password_reset_email(email, token)
            st.success("✅ Reset link sent! Please check your email.")
        except Exception as e:
            st.error("❌ Failed to send reset email.")
            st.exception(e)
