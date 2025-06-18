# app/pages/login.py

import streamlit as st
import sqlite3
import hashlib
import os
from dotenv import load_dotenv
from utils.tokens import generate_token

# Load environment variables
load_dotenv()
DB_PATH = st.secrets["USER_DB"]

# Page config
st.set_page_config(page_title="Login", layout="centered")
st.title("🔐 Login to YouTufy")

# Hash password securely
def hash_password(password: str) -> str:
    return hashlib.sha256(password.encode()).hexdigest()

# Authenticate user against database
def authenticate_user(email: str, password: str):
    try:
        conn = sqlite3.connect(DB_PATH)
        cur = conn.cursor()
        cur.execute("SELECT username, password, verified FROM users WHERE email=?", (email,))
        row = cur.fetchone()
        conn.close()
        if row:
            db_username, db_password, verified = row
            if hash_password(password) == db_password:
                return db_username, verified
    except Exception as e:
        st.error(f"⚠️ Login error: {e}")
    return None, False

# Login form
with st.form("login_form"):
    email = st.text_input("📧 Email", placeholder="Enter your email")
    password = st.text_input("🔑 Password", type="password", placeholder="Enter your password")
    login_button = st.form_submit_button("Login")

if login_button:
    if not email or not password:
        st.error("⚠️ Email and password are required.")
    else:
        username, verified = authenticate_user(email, password)
        if username:
            if not verified:
                st.error("❌ Your account is not verified. Please check your email.")
            else:
                st.session_state["user"] = email
                st.session_state["username"] = username
                st.success(f"✅ Welcome back, {username}!")
                st.switch_page("main")
        else:
            st.error("❌ Invalid email or password.")

# Divider
st.markdown("---")

# Forgot Password
if st.button("🔑 Forgot Password?"):
    st.switch_page("reset_password")

# Google Login
st.markdown("### Or login with Google")
if st.button("🔐 Continue with Google"):
    st.switch_page("google_login")
