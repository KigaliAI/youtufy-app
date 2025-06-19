# app/pages/login.py
import os
import sys
import streamlit as st
from dotenv import load_dotenv
from backend.auth import validate_user, get_user_by_email

load_dotenv()

st.set_page_config(page_title="Login – YouTufy", layout="centered")
st.title("🔐 Login to YouTufy")

# Login Form
with st.form("login_form"):
    email = st.text_input("Email")
    password = st.text_input("Password", type="password")
    submitted = st.form_submit_button("Login")

if submitted:
    if not email or not password:
        st.error("❗ Please fill in all fields.")
    elif not get_user_by_email(email):
        st.warning("⚠️ No user found with this email.")
    elif not validate_user(email, password):
        st.error("❌ Invalid email or password.")
    else:
        user_data = get_user_by_email(email)
        if user_data[4] == 0:
            st.warning("⚠️ Email not verified. Please check your inbox.")
            st.stop()

        st.session_state["user"] = email
        st.session_state["username"] = user_data[1]
        st.success(f"🎉 Welcome back, {user_data[1].capitalize()}!")
        st.switch_page("main")
