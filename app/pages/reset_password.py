# app/pages/reset_password.py

import os
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))
import sys
import sqlite3
import streamlit as st
import re
from utils.tokens import generate_token, verify_token, validate_token
import hashlib

# Set up project root
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
sys.path.insert(0, project_root)

# DB path
DB_PATH = st.secrets.get("USER_DB_PATH", "data/YouTufy_users.db")

st.set_page_config(page_title="Reset Password", layout="centered")

# -----------------------------------
# 🔍 Check if token is present
# -----------------------------------
query_token = st.query_params.get("token")

# Password hashing
def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

if query_token:
    st.title("🔐 Set New Password")

    with st.form("reset_password_form"):
        new_pass = st.text_input("New Password", type="password")
        confirm_pass = st.text_input("Confirm Password", type="password")
        submitted = st.form_submit_button("Update Password")

    if submitted:
        if not new_pass or not confirm_pass:
            st.error("❗ All fields are required.")
        elif new_pass != confirm_pass:
            st.error("❗ Passwords do not match.")
        else:
            try:
                conn = sqlite3.connect(DB_PATH)
                cur = conn.cursor()
                cur.execute("SELECT email FROM users")
                users = cur.fetchall()
                updated = False
                for (email,) in users:
                    stored_token = generate_token(email)
                    if verify_token(query_token, stored_token):
                        hashed = hash_password(new_pass)
                        cur.execute("UPDATE users SET password = ? WHERE email = ?", (hashed, email))
                        conn.commit()
                        st.success("✅ Password updated! You can now log in.")
                        st.page_link("/login", label="Go to Login", icon="➡️")
                        updated = True
                        break
                conn.close()

                if not updated:
                    st.error("❌ Invalid or expired token.")

            except Exception as e:
                st.error(f"❌ Error: {e}")

else:
    st.title("🔑 Reset Your YouTufy Password")
    st.markdown("We'll send a reset link to your registered email.")

    with st.form("request_reset_form"):
        email = st.text_input("Email")
        submitted = st.form_submit_button("Send Reset Link")

    if submitted:
        if not re.match(r"[^@]+@[^@]+\.[^@]+", email):
            st.error("❗ Invalid email address.")
        else:
            try:
                conn = sqlite3.connect(DB_PATH)
                cur = conn.cursor()
                cur.execute("SELECT * FROM users WHERE email=?", (email,))
                if cur.fetchone():
                    token = generate_token(email)
                    from utils.emailer import send_password_reset_email
                    send_password_reset_email(email, token)
                    st.success("📬 Reset link sent! Check your email.")
                else:
                    st.warning("⚠️ No account found with that email.")
                conn.close()
            except Exception as e:
                st.error(f"❌ Database error: {e}")
