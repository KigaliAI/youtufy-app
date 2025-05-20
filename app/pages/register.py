import os
import sys
import re
import hashlib
import sqlite3
from datetime import datetime, timedelta

import streamlit as st

# ✅ Adjust path for utility modules
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))
from utils.tokens import generate_token
from utils.emailer import send_registration_email

# ✅ Load DB path
DB_PATH = st.secrets.get("USER_DB_PATH", "data/YouTufy_users.db")

# 🔐 Hash password
def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

# 🔍 Check if user exists
def user_exists(email):
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("SELECT * FROM users WHERE email = ?", (email,))
    user = cur.fetchone()
    conn.close()
    return user is not None

# ✅ Register user
def register_user(email, username, password, token, expiry):
    try:
        conn = sqlite3.connect(DB_PATH)
        cur = conn.cursor()
        cur.execute("""
            INSERT INTO users (email, username, password, verified, token, token_expiry)
            VALUES (?, ?, ?, 0, ?, ?)
        """, (
            email,
            username,
            hash_password(password),
            token,
            expiry.strftime("%Y-%m-%d %H:%M:%S")
        ))
        conn.commit()
        conn.close()
        return True
    except Exception as e:
        st.error(f"❌ Registration failed: {e}")
        return False

# 🧾 UI
st.title("📝 Register for YouTufy")
st.markdown("Create a new account to manage your YouTube subscriptions.")

with st.form("registration_form"):
    email = st.text_input("📧 Email")
    username = st.text_input("👤 Username")
    password = st.text_input("🔒 Password", type="password")
    password2 = st.text_input("🔒 Confirm Password", type="password")
    submitted = st.form_submit_button("Register")

if submitted:
    if not email or not username or not password:
        st.error("❗ All fields are required.")
    elif not re.match(r"[^@]+@[^@]+\.[^@]+", email):
        st.error("❗ Invalid email address.")
    elif password != password2:
        st.error("❗ Passwords do not match.")
    elif user_exists(email):
        st.warning("⚠️ Email already registered. Try logging in.")
    else:
        token = generate_token(email)
        expiry = datetime.now() + timedelta(hours=1)
        success = register_user(email, username, password, token, expiry)
        if success:
            try:
                send_registration_email(email, username, token)
                st.success("✅ Registration successful! Check your email to verify your account.")
            except Exception as e:
                st.error("❌ Failed to send verification email.")
                st.exception(e)
