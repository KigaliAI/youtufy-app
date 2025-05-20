import os
import sys
import streamlit as st
import pandas as pd
from datetime import datetime
import time
from googleapiclient.discovery import build
import logging

# -------------------------------
# ✅ Set page config FIRST
# -------------------------------
st.set_page_config(page_title="YouTufy", layout="wide")

# -------------------------------
# ✅ Adjust backend import path
# -------------------------------
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "backend")))

# ✅ Import backend modules
try:
    from backend.auth import get_user_credentials, generate_auth_url_for_user
except ModuleNotFoundError:
    st.error("❌ Failed to import backend modules.")
    st.stop()

# ✅ Import utilities
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "utils")))
try:
    from utils.display import channel_card
except ModuleNotFoundError:
    def channel_card(row):
        st.write(f"**{row.get('snippet', {}).get('title', 'Unknown Channel')}**")

# -------------------------------
# 📡 Optimized Fetch Subscriptions
# -------------------------------
@st.cache_data(ttl=600)
def fetch_subscriptions(creds):
    youtube = build("youtube", "v3", credentials=creds)
    subscriptions = []

    request = youtube.subscriptions().list(
        part="snippet,contentDetails",
        mine=True,
        maxResults=50
    )

    channel_ids = []

    while request:
        response = request.execute()
        items = response.get("items", [])
        subscriptions.extend(items)
        for item in items:
            cid = item["snippet"]["resourceId"]["channelId"]
            channel_ids.append(cid)
        request = youtube.subscriptions().list_next(request, response)

    enriched_data = []
    for i in range(0, len(channel_ids), 50):
        batch_ids = channel_ids[i:i+50]
        stats_response = youtube.channels().list(
            part="statistics",
            id=",".join(batch_ids)
        ).execute()

        stats_map = {item["id"]: item["statistics"] for item in stats_response.get("items", [])}

        for sub in subscriptions[i:i+50]:
            cid = sub["snippet"]["resourceId"]["channelId"]
            sub["statistics"] = stats_map.get(cid, {})
        enriched_data.extend(subscriptions[i:i+50])

    return pd.DataFrame(enriched_data)

# -------------------------------
# 🖼️ Logo & Title (Improved UI)
# -------------------------------
col1, col2 = st.columns([1, 3])
with col1:
    st.image("assets/logo.jpeg", width=60)

with col2:
    st.markdown("<h1 style='margin-top: 10px;'>YouTufy – YouTube Subscriptions App</h1>", unsafe_allow_html=True)
    st.caption("🔒 Google OAuth Verified · Your data is protected")

st.markdown("<h2 style='color:#ff00ff;'>Welcome to YouTufy!</h2>", unsafe_allow_html=True)

st.markdown("""
    <div style='background-color:#f0f0f0; padding:15px; border-radius:6px; font-size:16px;'>
        🎥 **Youtufy securely accesses your YouTube subscriptions**.<br>
        🛡️ We request **youtube.readonly** permission to display your subscribed channels.<br>
        ✅ Click **Sign in with Google** to grant access and manage your subscriptions easily.
    </div>
""", unsafe_allow_html=True)

# 🔐 Sign-in Button
if st.button("🔐 Sign in with Google"):
    auth_url = generate_auth_url_for_user()
    st.markdown(f"[Click here to authenticate with Google]({auth_url})", unsafe_allow_html=True)

st.markdown("---")

# 👤 User session check
user_email = st.session_state.get("user")
username = st.session_state.get("username", "Guest")

if user_email:
    st.markdown(f"🎉 Welcome back, {username}!")

    if st.button("🔄 Refresh Subscriptions"):
        st.cache_data.clear()
        st.rerun()

    with st.spinner("📡 Loading your YouTube subscriptions..."):
        try:
            creds = get_user_credentials(user_email)
            start_time = time.time()
            df = fetch_subscriptions(creds)
            end_time = time.time()
            st.write(f"⏳ Subscriptions loaded in {end_time - start_time:.2f} seconds")
        except Exception as e:
            st.error("❌ Failed to authenticate or retrieve subscriptions.")
            st.exception(e)
            st.stop()

    if df.empty:
        st.warning("⚠️ No subscriptions found.")
        st.stop()

    st.metric("Total Channels", len(df))
    st.metric("Total Subscribers", f"{int(df['statistics.subscriberCount'].sum()):,}")
    st.metric("Total Videos", f"{int(df['statistics.videoCount'].sum()):,}")

    st.markdown("---")

    for _, row in df.iterrows():
        if isinstance(row.get("snippet"), dict):
            channel_card(row)

st.markdown("""
    <p style='text-align: center; font-size: 13px;'>🔐 Secure & Private | 
    <a href='https://www.youtufy.com/privacy' target='_blank'>Privacy Policy</a> | 
    <a href='https://www.youtufy.com/terms' target='_blank'>Terms of Service</a> | 
    <a href='https://www.youtufy.com/cookie' target='_blank'>Cookie Policy</a>
    </p>
""", unsafe_allow_html=True)
