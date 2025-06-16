# app/main.py
import streamlit as st
import sys
import os

# Ensure paths are correctly set for imports
sys.path.append(os.path.abspath(os.path.dirname(__file__)))
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app.controllers.dashboard import load_dashboard

# Configure the page layout
st.set_page_config(page_title="YouTufy", layout="wide")

# Retrieve user session data
user_email = st.session_state.get("user")
username = st.session_state.get("username")

if user_email and username:
    load_dashboard(user_email, username)
else:
    st.markdown("<h1 style='font-size:2.5rem; font-weight:bold; color:magenta; text-align: center;'>Welcome to YouTufy</h1>", unsafe_allow_html=True)
    st.markdown("<h2 style='font-size:1.8rem; font-weight:bold; color:magenta; text-align: center;'>Your YouTube Subscriptions System</h2>", unsafe_allow_html=True)

    st.markdown("<p style='font-size:1.1rem; color:magenta;'>YouTufy helps organize and manage your YouTube subscriptions in one place.</p>", unsafe_allow_html=True)
    st.markdown("<p style='font-size:1.1rem; color:magenta;'>🔒 Your data is protected · Google OAuth authentication required.</p>", unsafe_allow_html=True)

    st.markdown("""
    <p style='font-size:1.1rem; font-weight:bold; color:magenta;'>
    👉 <strong>Youtufy securely accesses your YouTube subscriptions</strong>.
    </p>
    """, unsafe_allow_html=True)

    st.markdown("<p style='font-size:1.1rem; font-weight:bold; color:magenta;'>✅ <strong>Choose one of the login methods:</strong></p>", unsafe_allow_html=True)

    # Authentication options
    col1, col2, col3 = st.columns(3)

    with col1:
        st.markdown("""
        <a href='/google_login' style='text-decoration: none;'>
            <div style='background-color: magenta; padding: 15px; border-radius: 10px; text-align: center;'>
                <span style='font-size:1.2rem; font-weight: bold; color: white;'>Continue with Google</span>
            </div>
        </a>
        """, unsafe_allow_html=True)

    with col2:
        st.markdown("""
        <a href='/login' style='text-decoration: none;'>
            <div style='background-color: magenta; padding: 15px; border-radius: 10px; text-align: center;'>
                <span style='font-size:1.2rem; font-weight: bold; color: white;'>Existing Account Login</span>
            </div>
        </a>
        """, unsafe_allow_html=True)

    with col3:
        st.markdown("""
        <a href='/register' style='text-decoration: none;'>
            <div style='background-color: magenta; padding: 15px; border-radius: 10px; text-align: center;'>
                <span style='font-size:1.2rem; font-weight: bold; color: white;'>Create Free Account</span>
            </div>
        </a>
        """, unsafe_allow_html=True)

    st.markdown("---")
    st.markdown("""
    <p style='text-align: center; font-size:20px;'>
    © 2025 YouTufy | <a href='https://www.youtufy.com/privacy.html' target='_blank'>Privacy Policy</a> |
    <a href='https://www.youtufy.com/terms.html' target='_blank'>Terms of Service</a> |
    <a href='https://www.youtufy.com/cookie.html' target='_blank'>Cookies</a>
    </p>
    """, unsafe_allow_html=True)

