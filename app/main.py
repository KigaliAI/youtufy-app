# app/main.py

import streamlit as st
import os
import sys

# Ensure correct module paths
sys.path.append(os.path.abspath(os.path.dirname(__file__)))
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app.controllers.dashboard import load_dashboard

# Configure page
st.set_page_config(page_title="YouTufy", layout="wide")

# Get user session state
user_email = st.session_state.get("user")
username = st.session_state.get("username")

# 🔐 Authenticated users → load dashboard
if user_email:
    load_dashboard(user_email, username)

# 🧭 Landing page for unauthenticated visitors
else:
    st.markdown("<h1 style='font-size:2.5rem; font-weight:bold; color:magenta; text-align: center;'>Welcome to YouTufy</h1>", unsafe_allow_html=True)
    st.markdown("<h2 style='font-size:1.8rem; font-weight:bold; color:magenta; text-align: center;'>Your YouTube Subscriptions System</h2>", unsafe_allow_html=True)

    st.markdown("<p style='font-size:1.1rem; color:magenta;'>YouTufy helps you organize and manage all your YouTube subscriptions in one place.</p>", unsafe_allow_html=True)
    st.markdown("<p style='font-size:1.1rem; color:magenta;'>🔒 Your data is protected – we only request read-only access via Google OAuth.</p>", unsafe_allow_html=True)
    st.markdown("<p style='font-size:1.1rem; font-weight:bold; color:magenta;'>✅ Choose one of the login methods below:</p>", unsafe_allow_html=True)

    # Login buttons
    col1, col2, col3 = st.columns(3)

    with col1:
        st.markdown("""
        <a href='/app/pages/google_login' style='text-decoration: none;'>
            <div style='background-color: magenta; padding: 15px; border-radius: 10px; text-align: center;'>
                <span style='font-size:1.2rem; font-weight: bold; color: white;'>🔐 Continue with Google</span>
            </div>
        </a>
        """, unsafe_allow_html=True)

    with col2:
        st.markdown("""
        <a href='/app/pages/login' style='text-decoration: none;'>
            <div style='background-color: magenta; padding: 15px; border-radius: 10px; text-align: center;'>
                <span style='font-size:1.2rem; font-weight: bold; color: white;'>🔑 Login</span>
            </div>
        </a>
        """, unsafe_allow_html=True)

    with col3:
        st.markdown("""
        <a href='/app/pages/register' style='text-decoration: none;'>
            <div style='background-color: magenta; padding: 15px; border-radius: 10px; text-align: center;'>
                <span style='font-size:1.2rem; font-weight: bold; color: white;'>🆕 Register</span>
            </div>
        </a>
        """, unsafe_allow_html=True)

    # Footer
    st.markdown("---")
    st.markdown("""
    <p style='text-align: center; font-size:16px;'>
        © 2025 YouTufy |
        <a href='https://www.youtufy.com/privacy.html' target='_blank'>Privacy Policy</a> |
        <a href='https://www.youtufy.com/terms.html' target='_blank'>Terms</a> |
        <a href='https://www.youtufy.com/cookie.html' target='_blank'>Cookies</a>
    </p>
    """, unsafe_allow_html=True)
