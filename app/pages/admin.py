# app/pages/admin.py
import os
import sys
import sqlite3
from datetime import datetime, timedelta

import streamlit as st

# Setup import paths for utils
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))
from utils.tokens import generate_token
from utils.emailer import send_registration_email

# 🔧 Page config
st.set_page_config(page_title="Admin – Invite Users", layout="centered")
st.title("🛠️ Admin Panel – Invite Users")

# 📁 Database path from secrets or default
DB_PATH = st.secrets["USER_DB"]

# 💌 Invitation Form
st.markdown("Invite users by email. They will receive a verification link to activate their account.")

with st.form("invite_user_form"):
    email = st.text_input("📧 User Email")
    username = st.text_input("👤 Optional Username", value="")
    submit = st.form_submit_button("Send Verification Email")

if submit:
    if not email:
        st.warning("⚠️ Please enter a valid email.")
    else:
        try:
            # 🔐 Generate token and expiration
            token = generate_token(email)
            expiry = datetime.now() + timedelta(hours=1)

            # 💾 Upsert user into database
            conn = sqlite3.connect(DB_PATH)
            cur = conn.cursor()
            cur.execute("""
                INSERT INTO users (email, username, verified, token, token_expiry)
                VALUES (?, ?, 0, ?, ?)
                ON CONFLICT(email) DO UPDATE SET
                    username = excluded.username,
                    token = excluded.token,
                    token_expiry = excluded.token_expiry,
                    verified = 0
            """, (
                email,
                username or email.split("@")[0],
                token,
                expiry.strftime('%Y-%m-%d %H:%M:%S')
            ))
            conn.commit()
            conn.close()

            # 📬 Send email
            send_registration_email(email, username, token)
            st.success(f"✅ Verification email sent to {email}")

        except Exception as e:
            st.error("❌ Failed to invite user.")
            st.exception(e)
