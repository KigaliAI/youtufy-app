# app/pages/verify_token.py
import os
import sys
import sqlite3
from datetime import datetime
import streamlit as st

# Setup system path for utility imports
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))
from utils.tokens import verify_token

# 🔧 Page & Environment Setup
st.set_page_config(page_title="Verify Email – YouTufy", layout="centered")
st.title("🔐 Email Verification")

DB_PATH = st.secrets["USER_DB"]
token = st.query_params.get("token")

if not token:
    st.warning("⚠️ Missing token in the URL.")
    st.stop()

# 📌 Handle Verification Logic
try:
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    cur.execute("SELECT email, token_expiry, verified FROM users WHERE token = ?", (token,))
    row = cur.fetchone()

    if not row:
        st.error("❌ Invalid or unknown verification token.")
        st.stop()

    email, expiry_str, verified = row

    if verified:
        st.success(f"✅ This email has already been verified: **{email}**")
        st.info("You can now log in to your account.")
        st.stop()

    if expiry_str:
        expiry = datetime.strptime(expiry_str, "%Y-%m-%d %H:%M:%S")
        if datetime.now() > expiry:
            st.error("⏰ This token has expired. Please request a new invitation.")
            st.stop()

    cur.execute("UPDATE users SET verified = 1 WHERE email = ?", (email,))
    conn.commit()

    st.success(f"✅ Email verified successfully: **{email}**")
    st.info("You can now log in to access your dashboard.")

    if st.button("🔐 Go to Login"):
        st.switch_page("login")

except Exception as e:
    st.error("❌ An error occurred during verification.")
    st.exception(e)

finally:
    conn.close()
