# app/pages/login.py
import streamlit as st
import sqlite3
import hashlib
from utils.tokens import generate_token
from dotenv import load_dotenv
import os


st.set_page_config(page_title="Login", layout="centered")
st.title("🔐 Login to YouTufy")

load_dotenv()
DB_PATH = os.getenv("USER_DB", "data/YouTufy_users.db")

# Hash pass and Authenticate user Functions
def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

def authenticate_user(email, password):
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("SELECT username, password, verified FROM users WHERE email=?", (email,))
    row = cur.fetchone()
    conn.close()
    if row:
        db_username, db_password, verified = row
        if hash_password(password) == db_password:
            return db_username, verified
    return None, False

# Email/Password Login Form
with st.form("login_form"):
    email = st.text_input("Email")
    password = st.text_input("Password", type="password")
    login_button = st.form_submit_button("Login")

if login_button:
    username, verified = authenticate_user(email, password)
    if username:
        if not verified:
            st.error("❌ Your account is not yet verified. Please check your email.")
        else:
            st.session_state.user = email
            st.session_state.username = username
            st.success(f"✅ Welcome back, {username}!")
            st.switch_page("main.py")
    else:
        st.error("❌ Invalid email or password.")

# Forgotten password Links
st.markdown("---")

if st.button("🔑 Forgot Password?"):
    st.switch_page("pages/reset_password.py")

# Google Login
st.markdown("### Or login with Google")
if st.button("🔐 Continue with Google"):
    st.switch_page("pages/google_login.py")
