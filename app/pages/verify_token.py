# app/pages/verify_token.py

import os
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))
import sqlite3
import streamlit as st
from utils.tokens import generate_token, verify_token, validate_token

# Add root path for imports
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
sys.path.insert(0, project_root)

st.set_page_config(page_title="Verify Email", layout="centered")
st.title("🔐 Email Verification")

DB_PATH = st.secrets.get("USER_DB_PATH", "data/YouTufy_users.db")

# -----------------------------------
# 📩 Get token from URL
# -----------------------------------
token = st.query_params.get("token")

if not token:
    st.warning("⚠️ Missing verification token in the URL.")
    st.stop()

try:
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("SELECT email FROM users")
    verified = False
    for (email,) in cur.fetchall():
        stored_token = generate_token(email)
        if verify_token(token, stored_token):
            cur.execute("UPDATE users SET verified = 1 WHERE email = ?", (email,))
            conn.commit()
            st.success(f"✅ Email verified: **{email}**")
            st.info("You can now log in.")
            
            # ✅ Fixed Login Navigation
            if st.button("Go to Login"):
                st.switch_page("pages.login")  # Use Streamlit navigation

            verified = True
            break
    conn.close()

    if not verified:
        st.error("❌ Invalid or expired token.")
except Exception as e:
    st.error("❌ Database error.")
    st.exception(e)
