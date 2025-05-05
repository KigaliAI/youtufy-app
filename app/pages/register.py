# app/pages/register.py
import streamlit as st
import sqlite3
from utils.tokens import generate_token
from utils.emailer import send_registration_email
import os
from dotenv import load_dotenv

load_dotenv()
DB_PATH = os.getenv("USER_DB_PATH", "data/YouTufy_users.db")

def user_exists(email):
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("SELECT * FROM users WHERE email = ?", (email,))
    user = cur.fetchone()
    conn.close()
    return user is not None

def register_user(email, username, password):
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("INSERT INTO users (email, username, password, verified) VALUES (?, ?, ?, 0)",
                (email, username, password))
    conn.commit()
    conn.close()

st.title("📝 Register for YouTufy")
st.markdown("Create a new account to manage your YouTube subscriptions.")

with st.form("registration_form"):
    email = st.text_input("Email")
    username = st.text_input("Username")
    password = st.text_input("Password", type="password")
    password2 = st.text_input("Confirm Password", type="password")
    submitted = st.form_submit_button("Register")

if submitted:
    if not email or not username or not password:
        st.error("❗ All fields are required.")
    elif password != password2:
        st.error("❗ Passwords do not match.")
    elif user_exists(email):
        st.warning("⚠️ Email already registered. Try logging in.")
    else:
        register_user(email, username, password)
        token = generate_token(email)
        send_registration_email(email, username, token)
        st.success("✅ Registration successful! Check your email to verify your account.")
