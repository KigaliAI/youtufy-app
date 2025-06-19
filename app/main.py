# app/main.py
import sys
import os

# Root directory to Python path
ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.append(ROOT_DIR)

import streamlit as st
import pandas as pd
from datetime import datetime

from backend.oauth import get_user_credentials, refresh_credentials
from backend.youtube import fetch_subscriptions
from app.components.channel_card import channel_card

# Configure Streamlit page
st.set_page_config(page_title="YouTufy", layout="wide")

# Session variables
user_email = st.session_state.get("user")
username = st.session_state.get("username")
google_creds_json = st.session_state.get("google_creds")
authenticated = st.session_state.get("authenticated", False)

# If user is authenticated, display dashboard
if user_email and google_creds_json and authenticated:
    st.markdown("<h1 style='font-size:1.8rem; font-weight:bold; color:magenta;'>📺 YouTufy – Your Dashboard</h1>", unsafe_allow_html=True)
    st.caption(f"🔒 Google OAuth Verified · Welcome, {username.capitalize()}!")

    creds = refresh_credentials(google_creds_json)

    with st.spinner("📡 Fetching YouTube subscriptions..."):
        df = fetch_subscriptions(creds, user_email)

    if df.empty or "snippet" not in df.columns or "statistics" not in df.columns:
        st.warning("⚠️ No subscriptions found or data unavailable.")
        st.stop()

    # Normalize numerical fields
    for col in ["statistics.subscriberCount", "statistics.videoCount", "statistics.viewCount"]:
        df[col] = pd.to_numeric(df.get(col, pd.Series(0)), errors="coerce").fillna(0)

    # Metrics summary
    st.metric("Total Channels", len(df))
    st.metric("Total Subscribers", f"{int(df['statistics.subscriberCount'].sum()):,}")
    st.metric("Total Videos", f"{int(df['statistics.videoCount'].sum()):,}")
    st.caption(f"📅 Last updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    st.markdown("---")

    # Render channel cards
    for _, row in df.iterrows():
        if isinstance(row.get("snippet"), dict):
            channel_card(row)

else:
    # Landing page (unauthenticated view)
    st.markdown("<h1 style='font-size:2.5rem; font-weight:bold; color:magenta; text-align: center;'>Welcome to YouTufy</h1>", unsafe_allow_html=True)
    st.markdown("<h2 style='font-size:1.8rem; font-weight:bold; color:magenta; text-align: center;'>Your YouTube Subscriptions System</h2>", unsafe_allow_html=True)

    st.markdown("<p style='font-size:1.1rem; color:magenta;'>Organize your favorite YouTube channels in one dashboard.</p>", unsafe_allow_html=True)
    st.markdown("<p style='font-size:1.1rem; color:magenta;'>🔒 Secure access via Google OAuth. We only request read-only permissions.</p>", unsafe_allow_html=True)

    st.markdown("<p style='font-size:1.1rem; font-weight:bold; color:magenta;'>✅ Choose a login method:</p>", unsafe_allow_html=True)

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
                <span style='font-size:1.2rem; font-weight: bold; color: white;'>Existing Account</span>
            </div>
        </a>
        """, unsafe_allow_html=True)

    with col3:
        st.markdown("""
        <a href='/register' style='text-decoration: none;'>
            <div style='background-color: magenta; padding: 15px; border-radius: 10px; text-align: center;'>
                <span style='font-size:1.2rem; font-weight: bold; color: white;'>Create Account</span>
            </div>
        </a>
        """, unsafe_allow_html=True)

    st.markdown("---")
    st.markdown("""
    <p style='text-align: center; font-size:18px;'>
    © 2025 YouTufy |
    <a href='https://www.youtufy.com/privacy.html' target='_blank'>Privacy</a> ·
    <a href='https://www.youtufy.com/terms.html' target='_blank'>Terms</a> ·
    <a href='https://www.youtufy.com/cookie.html' target='_blank'>Cookies</a>
    </p>
    """, unsafe_allow_html=True)
