import os
import sys
import streamlit as st
import pandas as pd
from datetime import datetime
import time
from googleapiclient.discovery import build
import logging
from backend.auth import get_user_credentials  # ✅ Ensures authentication support

# -------------------------------
# ✅ Set page config FIRST
# -------------------------------
st.set_page_config(page_title="YouTufy", layout="wide")

# -------------------------------
# 🏷️ Ensure users are logged in (Redirects to login.py)
# -------------------------------
user_email = st.session_state.get("user")
username = st.session_state.get("username", "Guest")

if not user_email:
    st.warning("🔐 Please sign in to access your subscriptions.")

    st.markdown("""
    👉 <strong>Youtufy securely accesses your YouTube subscriptions</strong>.<br>
    🛡️ We request <code>youtube.readonly</code> permission.<br>
    ✅ Choose one of the login methods below:
    """, unsafe_allow_html=True)

    st.page_link("pages/login.py", label="Classic Login (Email & Password)", icon="✉️")
    st.page_link("pages/google_login.py", label="Sign in with Google", icon="🔐")
    st.stop()

# ✅ Continue if authenticated
else:
    creds = get_user_credentials(user_email)
    st.success(f"✅ Welcome back, {username}!")

# -------------------------------
# 📡 Fetch Subscriptions (Logging Added)
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

    # 🔄 Enrich with channel statistics
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

    logging.info(f"✅ Subscriptions fetched for user: {user_email}")  # ✅ Debugging fix
    return pd.DataFrame(enriched_data)

# -------------------------------
# 🖼️ UI: Logo & Welcome Message
# -------------------------------
col1, col2 = st.columns([1, 3])
with col1:
    st.image("assets/logo.jpeg", width=60)

with col2:
    st.markdown("<h1 style='margin-top: 10px;'>YouTufy – YouTube Subscriptions App</h1>", unsafe_allow_html=True)
    st.caption("🔒 Google OAuth Verified · Your data is protected")

st.markdown("""
    <div style='background-color:#f0f0f0; padding:15px; border-radius:6px; font-size:16px;'>
        🎥 **Youtufy securely accesses your YouTube subscriptions**.<br>
        🛡️ We request **youtube.readonly** permission to display your subscribed channels.<br>
        ✅ Click **Sign in with Google** to grant access and manage your subscriptions easily.
    </div>
""", unsafe_allow_html=True)

# ✅ Redirect "Sign in with Google" to login.py for authentication
if st.button("🔐 Sign in with Google"):
    st.switch_page("pages/login.py")  # ✅ Redirect users to login page

st.markdown("---")

# ✅ Refresh Button
if st.button("🔄 Refresh Subscriptions"):
    st.cache_data.clear()
    st.rerun()

# 📡 Subscription Loading
with st.spinner("📡 Fetching subscriptions..."):
    try:
        start_time = time.time()
        df = fetch_subscriptions(creds)
        end_time = time.time()
        st.write(f"⏳ Subscriptions loaded in {end_time - start_time:.2f} seconds")
    except Exception as e:
        st.error("❌ Failed to load subscriptions.")
        st.exception(e)
        st.stop()

if df.empty:
    st.warning("⚠️ No subscriptions found.")
else:
    st.metric("Total Channels", len(df))

    try:
        df["subscribers"] = pd.to_numeric(df["statistics"].apply(lambda s: s.get("subscriberCount", 0)), errors="coerce")
        df["videos"] = pd.to_numeric(df["statistics"].apply(lambda s: s.get("videoCount", 0)), errors="coerce")
        df["views"] = pd.to_numeric(df["statistics"].apply(lambda s: s.get("viewCount", 0)), errors="coerce")

        st.metric("Total Subscribers", f"{int(df['subscribers'].sum()):,}")
        st.metric("Total Videos", f"{int(df['videos'].sum()):,}")
    except Exception as e:
        st.warning("⚠️ Could not display metrics. Stats missing.")

    st.caption(f"📅 Last updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    for _, row in df.iterrows():
        title = row.get("snippet", {}).get("title", "Unknown")
        st.markdown(f"- **{title}**")

# ✅ Privacy & Terms Links
st.markdown("""
    <p style='text-align: center; font-size: 13px;'>🔐 Secure & Private |
    <a href='https://www.youtufy.com/privacy' target='_blank'>Privacy Policy</a> |
    <a href='https://www.youtufy.com/terms' target='_blank'>Terms of Service</a> |
    <a href='https://www.youtufy.com/cookie' target='_blank'>Cookie Policy</a>
    </p>
""", unsafe_allow_html=True)

