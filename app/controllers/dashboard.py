# app/controllers/dashboard.py
import streamlit as st
import pandas as pd
from datetime import datetime
from backend.youtube import fetch_subscriptions
from app.components.channel_card import channel_card
from backend.auth import get_user_credentials

def load_dashboard(user_email, username):
    st.markdown("<h1 style='font-size:1.8rem; font-weight:bold; color:magenta;'>YouTufy – Your YouTube Subscriptions Dashboard</h1>", unsafe_allow_html=True)
    st.caption("🔒 Your data is protected · Access granted via Google OAuth (`youtube.readonly`)")
    st.success(f"🎉 Welcome back, {username.capitalize()}!")

    with st.spinner("📡 Loading your YouTube subscriptions..."):
        creds = get_user_credentials(user_email)
        df = fetch_subscriptions(creds, user_email)

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
