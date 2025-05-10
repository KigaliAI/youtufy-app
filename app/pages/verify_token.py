# app/pages/verify_token.py

import os
import sys
import sqlite3
import streamlit as st

# ✅ Add backend/utils directory to the path
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
utils_path = os.path.join(project_root, "utils")
sys.path.insert(0, utils_path)

from tokens import validate_token  # This works now since utils is in path

# Page config
st.set_page_config(page_title="Verify Account", layout="centered")
st.title("🔐 Verify Your Email")

# -----------------------------------
# 📩 Get token from URL query params
# -----------------------------------
token = st.query_params.get("token")

if not token:
    st.warning("⚠️ Missing verification token in the URL.")
    st.stop()

# -----------------------------------
# 🔐 Validate token content
# -----------------------------------
email = validate_token(token)

if not email:
    st.error("❌ Invalid or expired token. Please request a new verification link.")
    st.stop()

# -----------------------------------
# 📦 Update user verification status
# -----------------------------------
DB_PATH = st.secrets.get("USER_DB_PATH", "data/YouTufy_users.db")

try:
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("UPDATE users SET verified = 1 WHERE email = ?", (email,))
    conn.commit()
    conn.close()

    st.success(f"✅ Email verified successfully for: **{email}**")
    st.info("You can now return to the app and log in.")
    st.page_link("/login", label="Go to Login", icon="➡️")

except Exception as e:
    st.error("❌ Failed to update your verification status. Please try again later.")
    st.exception(e)
