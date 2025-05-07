# app/pages/reset_password.py
import streamlit as st
import sqlite3
import re
from utils.tokens import generate_token
from utils.emailer import send_password_reset_email

# Page setup
st.set_page_config(page_title="Reset Password", layout="centered")
st.title("🔑 Reset Your YouTufy Password")

# Load DB path from secrets (fallback to dev path)
DB_PATH = st.secrets.get("USER_DB_PATH", "data/YouTufy_users.db")

# -------------------------------------
# 📬 Email validation helper
# -------------------------------------
def is_valid_email(email):
    return re.match(r"[^@]+@[^@]+\.[^@]+", email)

# -------------------------------------
# 📦 Database access helper
# -------------------------------------
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
# 🧾 UI form
# -------------------------------------
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
