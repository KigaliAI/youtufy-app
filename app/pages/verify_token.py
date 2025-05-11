# app/pages/verify_token.py

import os
import sqlite3
import streamlit as st
from utils.tokens import validate_token

# ✅ Configure the page
st.set_page_config(page_title="Verify Account", layout="centered")
st.title("🔐 Email Verification")

# ✅ Token from URL
token = st.query_params.get("token")
if not token:
    st.warning("⚠️ Missing verification token in the URL.")
    st.stop()

# ✅ Validate the token
email = validate_token(token)
if not email:
    st.error("❌ Invalid or expired token. Please request a new verification link.")
    st.stop()

# ✅ Load DB path securely
DB_PATH = st.secrets.get("USER_DB_PATH", "data/YouTufy_users.db")

# ✅ Update user verification
try:
    with sqlite3.connect(DB_PATH) as conn:
        cur = conn.cursor()
        cur.execute("UPDATE users SET verified = 1, token = NULL WHERE email = ?", (email,))
        conn.commit()

    st.success(f"✅ Email verified for: **{email}**")
    st.info("You may now return to the app and log in.")
    st.page_link("/login", label="🔐 Go to Login", icon="➡️")

except Exception as e:
    st.error("❌ Failed to update your verification status.")
    st.exception(e)
