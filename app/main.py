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
# 📡 Fetch & Enrich YouTube Subscriptions
# -------------------------------
@st.cache_data(ttl=600)
def fetch_subscriptions(creds, user_email=None):
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

    df = pd.DataFrame(enriched_data)

    # ✅ Avoid NaN issues in numeric conversions
    for col in ['subscriberCount', 'videoCount', 'viewCount']:
        df[f'statistics.{col}'] = pd.to_numeric(
            df['statistics'].apply(lambda s: s.get(col) if isinstance(s, dict) else 0),
            errors='coerce'
        ).fillna(0)

    return df

# -------------------------------
# 🖼️ UI Setup
# -------------------------------
st.markdown("<h1>YouTufy – YouTube Subscriptions App</h1>", unsafe_allow_html=True)

# 🔐 Sign-in Button
if st.button("🔐 Sign in with Google"):
    user_email = st.session_state.get("user", "temp@placeholder.com")  # Dynamically use logged-in user
    auth_url = generate_auth_url_for_user(user_email)
    st.markdown(f"[Click here to authenticate with Google]({auth_url})", unsafe_allow_html=True)

# -------------------------------
# 👤 Dashboard
# -------------------------------
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
            start = time.time()
            df = fetch_subscriptions(creds, user_email)
            end = time.time()
            st.write(f"⏳ Subscriptions loaded in {end - start:.2f} seconds")
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

# Footer
st.markdown("🔐 Secure & Private | [Privacy Policy](https://www.youtufy.com/privacy)")

