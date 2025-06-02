#app/pages/google_login.py
# app/pages/google_login.py

import os
import streamlit as st
import pandas as pd
from datetime import datetime
from dotenv import load_dotenv

from backend.oauth import (
    get_user_credentials,
    store_oauth_credentials,
    get_flow,
    get_credentials_from_code,
    refresh_credentials,
)
from backend.youtube import fetch_subscriptions
from app.components import channel_card

# Page setup
st.set_page_config(page_title="YouTufy – Dashboard", layout="wide")
st.title("🌍 Sign in with Google")

# Load env vars
load_dotenv()
REDIRECT_URI = "https://youtufy-one.streamlit.app/app/pages/google_login"  # Must match Google Console

# Session vars
user_email = st.session_state.get("user")
username = st.session_state.get("username")
authenticated = st.session_state.get("authenticated", False)

# Handle OAuth redirect with code
if "code" in st.query_params and not authenticated:
    st.info("🔁 Exchanging code for tokens...")
    try:
        code = st.query_params["code"]
        creds = get_credentials_from_code(code, REDIRECT_URI)
        user_email = creds.id_token.get("email")

        if not user_email:
            st.error("❌ Google login failed: No email returned.")
            st.stop()

        # Store session info
        st.session_state["user"] = user_email
        st.session_state["username"] = user_email.split("@")[0]
        st.session_state["google_creds"] = creds.to_json()
        st.session_state["authenticated"] = True

        # Save token to disk
        store_oauth_credentials(creds, user_email)

        st.success("✅ Login successful. Reloading dashboard...")
        st.rerun()
    except Exception as e:
        st.error("❌ Google OAuth failed during token exchange.")
        st.exception(e)
        st.stop()

# If not authenticated, prompt login
if not st.session_state.get("authenticated"):
    flow = get_flow(REDIRECT_URI)
    auth_url, _ = flow.authorization_url(prompt="consent", access_type="offline")

    st.markdown(f"""
        <p style="text-align:center; margin-top: 20px;">
            <a href="{auth_url}" style="
                padding: 14px 24px;
                background-color: #8F00FF;
                color: white;
                text-decoration: none;
                border-radius: 6px;
                font-weight: bold;">
                🔐 Sign in with Google
            </a>
        </p>
    """, unsafe_allow_html=True)
    st.stop()

# Authenticated → fetch dashboard
st.markdown("<h1 style='font-size:1.8rem; font-weight:bold; color:magenta;'>YouTufy – Your YouTube Subscriptions Dashboard</h1>", unsafe_allow_html=True)
st.caption("🔒 Google OAuth Verified · Your data is protected")
st.success(f"🎉 Welcome back, {st.session_state.username.capitalize()}!")

# Safely refresh credentials
if not st.session_state.get("google_creds"):
    st.error("⚠️ No Google credentials in session. Please login again.")
    st.stop()

creds = refresh_credentials(st.session_state["google_creds"])
st.session_state["google_creds"] = creds.to_json()

# Fetch YouTube subscriptions
with st.spinner("📡 Loading your YouTube subscriptions..."):
    df = fetch_subscriptions(creds, user_email)

if df.empty or 'statistics' not in df.columns or 'snippet' not in df.columns:
    st.warning("⚠️ No subscriptions found.")
    st.stop()

# Clean & normalize
for col in ['statistics.subscriberCount', 'statistics.videoCount', 'statistics.viewCount']:
    df[col] = pd.to_numeric(df.get(col, 0), errors='coerce').fillna(0)

df = df[df['snippet'].notna() & df['statistics'].notna()]

# Summary metrics
st.metric("Total Channels", len(df))
st.metric("Total Subscribers", f"{int(df['statistics.subscriberCount'].sum()):,}")
st.metric("Total Videos", f"{int(df['statistics.videoCount'].sum()):,}")
st.caption(f"📅 Last updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

st.markdown("---")

# Display each channel
for _, row in df.iterrows():
    if isinstance(row.get("snippet"), dict):
        channel_card(row)

