import os
import sys
import sqlite3
from datetime import datetime
import streamlit as st

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

from utils.tokens import verify_token

st.set_page_config(page_title="Verify Email", layout="centered")
st.title("🔐 Email Verification")

DB_PATH = st.secrets.get("USER_DB_PATH", "data/YouTufy_users.db")

token = st.query_params.get("token")

if not token:
    st.warning("⚠️ Missing token in the URL.")
    st.stop()

try:
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    cur.execute("SELECT email, token_expiry, verified FROM users WHERE token = ?", (token,))
    row = cur.fetchone()

    if not row:
        st.error("❌ Invalid or unknown verification token.")
        st.stop()

    email, expiry_str, verified = row

    if verified == 1:
        st.success(f"✅ This email has already been verified: **{email}**")
        st.info("You can now log in.")
        st.stop()

    if expiry_str:
        expiry = datetime.strptime(expiry_str, "%Y-%m-%d %H:%M:%S")
        if datetime.now() > expiry:
            st.error("⏰ This token has expired. Please ask the admin to re-invite you.")
            st.stop()

    cur.execute("UPDATE users SET verified = 1 WHERE email = ?", (email,))
    conn.commit()
    st.success(f"✅ Email verified: **{email}**")
    st.info("You can now log in and access your dashboard.")

    if st.button("🔐 Go to Login"):
        st.switch_page("pages/login.py")

except Exception as e:
    st.error("❌ An error occurred during verification.")
    st.exception(e)
finally:
    conn.close()

