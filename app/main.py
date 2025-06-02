import streamlit as st
import sys
import os

sys.path.append(os.path.abspath(os.path.dirname(__file__)))
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app.controllers.dashboard import load_dashboard

st.set_page_config(page_title="YouTufy", layout="wide")

# Ensure session state variables exist to prevent errors
user_email = st.session_state.get("user", None)
username = st.session_state.get("username", None)

if user_email:
    load_dashboard(user_email, username)
else:
    st.markdown("<h1 style='font-size:2.5rem; font-weight:bold; color:magenta; text-align: center;'>Welcome to YouTufy</h1>", unsafe_allow_html=True)
    st.markdown("<h2 style='font-size:1.8rem; font-weight:bold; color:magenta; text-align: center;'>Your YouTube Subscriptions System</h2>", unsafe_allow_html=True)

    st.markdown("<p style='font-size:1.1rem; color:magenta;'>YouTufy App helps you to organize and manage all your YouTube subscriptions in one place.</p>", unsafe_allow_html=True)

    st.markdown("<p style='font-size:1.1rem; color:magenta;'>🔒 Your data is protected · Access granted via Google OAuth ('youtube.readonly' permission)</p>", unsafe_allow_html=True)

    st.markdown("<p style='font-size:1.1rem; font-weight:bold; color:magenta;'>✅ <strong>Choose one of the login methods:</strong></p>", unsafe_allow_html=True)

    # Improved button layout for responsiveness
    col1, col2, col3 = st.columns([1, 1, 1])

    with col1:
        if st.button("🔐 Continue with Google"):
            st.switch_page("google_login")

    with col2:
        if st.button("🔑 Existing Account Login"):
            st.switch_page("login")

    with col3:
        if st.button("🆕 Create Free Account"):
            st.switch_page("register")

    # Footer
    st.markdown("---")
    st.markdown("""
    <p style='text-align: center; font-size:20px;'>
    © 2025 YouTufy | <a href='https://www.youtufy.com/privacy.html' target='_blank'>Privacy Policy</a> |
    <a href='https://www.youtufy.com/terms.html' target='_blank'>Terms of Service</a> |
    <a href='https://www.youtufy.com/cookie.html' target='_blank'>Cookies</a>
    </p>
    """, unsafe_allow_html=True)
