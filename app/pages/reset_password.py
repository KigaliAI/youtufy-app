# app/pages/reset_password.py

import streamlit as st
import sqlite3
import hashlib
import re
from utils.tokens import generate_token, validate_token
from utils.emailer import send_password_reset_email

# Page setup
st.set_page_config(page_title="Reset Password", layout="centered")
st.title("🔑 Reset Your YouTufy Password")

DB_PATH = st.secrets.get("USER_DB_PATH", "data/YouTufy_users.db")


def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()


def is_valid_email(email):
    return re.match(r"[^@]+@[^@]+\.[^@]+", email)


def get_user_by_email(email):
    try:
        conn = sqlite3.connect(DB_PATH)
        cur = conn.cursor()
        cur.execute("SELECT email FROM users WHERE email=?", (email,))
        result = cur.fetchone()
        conn.close()
        return result is not None
    except Exception as e:
        st.error(f"❌ Failed to access database: {e}")
        return False


# -------------------------------------
# 🔁 Check if user is here via token link
# -------------------------------------
token = st.query_params.get("token")

if token:
    # Handle token-based reset
    email = validate_token(token)

    if not email:
        st.error("❌ Invalid or expired token. Please request a new password reset.")
        st.stop()

    st.subheader("🔐 Set a New Password")
    with st.form("new_password_form"):
        new_pass = st.text_input("New Password", type="password")
        confirm_pass = st.text_input("Confirm Password", type="password")
        submitted = st.form_submit_button("Update Password")

    if submitted:
        if not new_pass or not confirm_pass:
            st.error("❗ Please fill in both password fields.")
        elif new_pass != confirm_pass:
            st.error("❗ Passwords do not match.")
        else:
            try:
                conn = sqlite3.connect(DB_PATH)
                cur = conn.cursor()
                cur.execute("UPDATE users SET password = ? WHERE email = ?", (hash_password(new_pass), email))
                conn.commit()
                conn.close()
                st.success("✅ Password updated successfully!")
                st.page_link("/login", label="Go to Login", icon="➡️")
            except Exception as e:
                st.error("❌ Failed to update password.")
                st.exception(e)
else:
    # Show email input for reset link
    st.subheader("📧 Request a Password Reset")
    with st.form("reset_form"):
        email = st.text_input("Enter your registered email")
        submitted = st.form_submit_button("Send Reset Link")

    if submitted:
        if not is_valid_email(email):
            st.error("❗ Please enter a valid email address.")
        elif not get_user_by_email(email):
            st.warning("⚠️ No account found with that email.")
        else:
            try:
                token = generate_token(email)
                send_password_reset_email(email, token)
                st.success("✅ Reset link sent! Please check your email.")
            except Exception as e:
                st.error(f"❌ Failed to send reset email: {e}")
