# app/pages/dashboard.py

import os
import json
import streamlit as st
import pandas as pd
from datetime import datetime

from backend.auth import store_oauth_credentials
from backend.youtube import fetch_subscriptions
from backend.oauth import get_flow, get_credentials_from_code, refresh_credentials
from app.components import channel_card

st.set_page_config(page_title="YouTufy – Dashboard", layout="wide")

REDIRECT_URI = "https://youtufy-one.streamlit.app/dashboard"

# 🔐 Session & OAuth Handling
user_email = st.session_state.get("user")
username = st.session_state.get("username")
google_creds_json = st.session_state.get("google_creds")
creds = None

if user_email and google_creds_json:
    creds = refresh_credentials(google_creds_json)
    st.session_state["google_creds"] = creds.to_json()
    st.session_state["authenticated"] = True

elif st.query_params.get("code"):
    try:
        code = st.query_params["code"]
        creds = get_credentials_from_code(code, REDIRECT_URI)
        user_email = creds.id_token.get("email")

        if not user_email:
            st.error("❌ Google login failed: No email found.")
            st.stop()

        st.session_state["user"] = user_email
        st.session_state["username"] = user_email.split("@")[0]
        st.session_state["google_creds"] = creds.to_json()
        st.session_state["authenticated"] = True
        store_oauth_credentials(creds, user_email)

        st.success(f"✅ Logged in as {user_email}")

    except Exception as e:
        st.error("❌ Google OAuth flow failed.")
        st.exception(e)
        st.stop()
else:
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

# ✅ Dashboard UI
if st.session_state.get("authenticated"):
    st.markdown("<h1 style='font-size:1.8rem; font-weight:bold; color:magenta;'>YouTufy – Your YouTube Subscriptions Dashboard</h1>", unsafe_allow_html=True)
    st.caption("🔒 Google OAuth Verified · Your data is protected")
    st.success(f"🎉 Welcome back, {st.session_state.username.capitalize()}!")

    with st.spinner("📡 Loading your YouTube subscriptions..."):
        df = fetch_subscriptions(creds, st.session_state["user"])

    if df.empty or 'statistics' not in df.columns or 'snippet' not in df.columns:
        st.warning("⚠️ No subscriptions found.")
        st.stop()

    for col in ['statistics.subscriberCount', 'statistics.videoCount', 'statistics.viewCount']:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors='coerce')
        else:
            df[col] = 0

    df = df[df['snippet'].notna() & df['statistics'].notna()]

    st.metric("Total Channels", len(df))
    st.metric("Total Subscribers", f"{int(df['statistics.subscriberCount'].sum()):,}")
    st.metric("Total Videos", f"{int(df['statistics.videoCount'].sum()):,}")
    st.caption(f"📅 Last updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

    st.markdown("---")

    for _, row in df.iterrows():
        if isinstance(row.get("snippet"), dict):
            channel_card(row)
