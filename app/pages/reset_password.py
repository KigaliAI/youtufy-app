# app/pages/reset_password.py
import streamlit as st
import sqlite3
import os
from dotenv import load_dotenv
from utils.tokens import generate_token
from utils.emailer import send_password_reset_email

st.set_page_config(page_title="Reset Password", layout="centered")
st.title("🔑 Reset Your YouTufy Password")

load_dotenv()
DB_PATH = os.getenv("USER_DB", "data/YouTufy_users.db")

with st.form("reset_form"):
    email = st.text_input("Enter your registered email")
    submitted = st.form_submit_button("Send Reset Link")

if submitted:
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("SELECT email FROM users WHERE email=?", (email,))
    if cur.fetchone():
        token = generate_token(email)
        send_password_reset_email(email, token)
        st.success("✅ Reset link sent! Please check your email.")
    else:
        st.warning("⚠️ No account found with that email.")
