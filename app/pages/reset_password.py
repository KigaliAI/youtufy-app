import os
import sys
import re
import sqlite3
import hashlib
from datetime import datetime, timedelta
import streamlit as st

# Add project root for imports
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))
from utils.tokens import generate_token, verify_token
from utils.emailer import send_password_reset_email

DB_PATH = st.secrets.get("USER_DB_PATH", "data/YouTufy_users.db")
st.set_page_config(page_title="Reset Password", layout="centered")

# 🔐 Password hasher
def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

# 🌐 Get reset token from URL
query_token = st.query_params.get("token")

# ---------------------------
# 🔁 Password Reset Flow
# ---------------------------
if query_token:
    st.title("🔐 Set a New Password")

    try:
        conn = sqlite3.connect(DB_PATH)
        cur = conn.cursor()
        cur.execute("SELECT email, reset_expiry FROM users WHERE reset_token = ?", (query_token,))
        row = cur.fetchone()

        if not row:
            st.error("❌ Invalid or expired token.")
            conn.close()
        else:
            email, expiry_str = row
            if datetime.strptime(expiry_str, "%Y-%m-%d %H:%M:%S") < datetime.now():
                st.error("⏰ This token has expired.")
                conn.close()
            else:
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
                        hashed = hash_password(new_pass)
                        cur.execute("UPDATE users SET password = ?, reset_token = NULL, reset_expiry = NULL WHERE email = ?", (hashed, email))
                        conn.commit()
                        conn.close()
                        st.success("✅ Password updated! You can now log in.")
                        st.page_link("pages/login.py", label="Go to Login", icon="➡️")
    except Exception as e:
        st.error(f"❌ Error: {e}")

# ---------------------------
# 📨 Request Reset Link Flow
# ---------------------------
else:
    st.title("🔑 Reset Your YouTufy Password")
    st.markdown("We'll send a reset link to your registered email address.")

    with st.form("request_reset_form"):
        email = st.text_input("📧 Email")
        submitted = st.form_submit_button("Send Reset Link")

    if submitted:
        if not re.match(r"[^@]+@[^@]+\.[^@]+", email):
            st.error("❗ Invalid email address.")
        else:
            try:
                conn = sqlite3.connect(DB_PATH)
                cur = conn.cursor()
                cur.execute("SELECT * FROM users WHERE email = ?", (email,))
                if cur.fetchone():
                    token = generate_token(email)
                    expiry = datetime.now() + timedelta(hours=1)

                    # Store token and expiry
                    cur.execute("UPDATE users SET reset_token = ?, reset_expiry = ? WHERE email = ?", (
                        token,
                        expiry.strftime("%Y-%m-%d %H:%M:%S"),
                        email
                    ))
                    conn.commit()
                    conn.close()

                    # Send reset link
                    send_password_reset_email(email, token)
                    st.success("📬 Reset link sent! Check your email.")
                else:
                    st.warning("⚠️ No account found with that email.")
            except Exception as e:
                st.error(f"❌ Database error: {e}")
