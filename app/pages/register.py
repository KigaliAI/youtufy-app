# app/pages/register.py
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))
import sqlite3
import streamlit as st
from dotenv import load_dotenv
from utils.tokens import generate_token
from utils.emailer import send_registration_email
from backend.auth import hash_password  # reuse existing hashing logic

# 🔧 Load environment
load_dotenv()
DB_PATH = st.secrets["USER_DB"]

# 🔍 Check if user already exists
def user_exists(email: str) -> bool:
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("SELECT 1 FROM users WHERE email = ?", (email,))
    exists = cur.fetchone() is not None
    conn.close()
    return exists

# 🧾 Insert user into DB (unverified by default)
def register_user(email: str, username: str, password: str):
    hashed_pw = hash_password(password)
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("""
        INSERT INTO users (email, username, password, verified)
        VALUES (?, ?, ?, 0)
    """, (email, username, hashed_pw))
    conn.commit()
    conn.close()

# 🖥️ Page UI
st.set_page_config(page_title="Register – YouTufy", layout="centered")
st.title("📝 Register for YouTufy")
st.markdown("Create a new account to manage your YouTube subscriptions in one place.")

# 📥 Registration Form
with st.form("registration_form"):
    email = st.text_input("📧 Email")
    username = st.text_input("👤 Username")
    password = st.text_input("🔐 Password", type="password")
    password2 = st.text_input("🔐 Confirm Password", type="password")
    submitted = st.form_submit_button("Register")

# 📤 Form Submission Logic
if submitted:
    if not all([email, username, password, password2]):
        st.error("❗ All fields are required.")
    elif password != password2:
        st.error("❗ Passwords do not match.")
    elif user_exists(email):
        st.warning("⚠️ Email already registered. Try logging in.")
    else:
        try:
            register_user(email, username, password)
            token = generate_token(email)
            send_registration_email(email, username, token)
            st.success("✅ Registration successful! Check your email to verify your account.")
        except Exception as e:
            st.error("❌ Something went wrong during registration.")
            st.exception(e)
