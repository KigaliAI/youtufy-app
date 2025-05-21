import os
import sys
import streamlit as st
import pandas as pd
from datetime import datetime
import time
from googleapiclient.discovery import build

# -------------------------------
# ✅ Page Configuration
# -------------------------------
st.set_page_config(page_title="YouTufy", layout="wide")

# -------------------------------
# ✅ Import Backend Modules
# -------------------------------
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "backend")))
from backend.auth import get_user_credentials

# -------------------------------
# ✅ Check User Session
# -------------------------------
user_email = st.session_state.get("user")
username = st.session_state.get("username", "Guest")

if not user_email:
    st.error("🔒 You need to sign in first!")
    st.switch_page("pages/login.py")

# -------------------------------
# ✅ Fetch Google Credentials
# -------------------------------
creds = get_user_credentials(user_email)

# -------------------------------
# 🖼️ UI – Header & Intro
# -------------------------------
col1, col2 = st.columns([1, 3])
with col1:
    st.image("assets/logo.jpeg", width=60)

with col2:
    st.markdown("<h1 style='margin-top: 10px;'>YouTufy – YouTube Subscriptions App</h1>", unsafe_allow_html=True)
    st.caption("🔒 Google OAuth Verified · Your data is protected")

st.markdown(f"""
    <div style='background-color:#f0f0f0; padding:15px; border-radius:6px; font-size:16px;'>
        🎥 Welcome, <strong>{username}</strong>!<br>
        ✅ Your YouTube subscriptions will load securely via Google.
    </div>
""", unsafe_allow_html=True)

st.markdown("---")

# -------------------------------
# ✅ Subscription Fetch Function
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

    while request:
        response = request.execute()
        subscriptions.extend(response.get("items", []))
        request = youtube.subscriptions().list_next(request, response)

    return pd.DataFrame(subscriptions)

# -------------------------------
# 📡 Load Subscriptions
# -------------------------------
with st.spinner("📡 Loading your YouTube subscriptions..."):
    try:
        start_time = time.time()
        df = fetch_subscriptions(creds)
        end_time = time.time()
        st.write(f"⏳ Loaded in {end_time - start_time:.2f} seconds")
    except Exception as e:
        st.error("❌ Failed to load subscriptions.")
        st.exception(e)
        st.stop()

if df.empty or 'snippet' not in df.columns:
    st.warning("⚠️ No subscriptions found.")
    st.stop()

# -------------------------------
# 📊 Display Metrics
# -------------------------------
st.metric("Total Channels", len(df))

# YouTube API may not provide full stats without another call.
# So, skipping subscriberCount / videoCount for now unless added.

st.caption(f"📅 Last updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
st.markdown("---")

# -------------------------------
# 🖼️ Display Channels
# -------------------------------
for _, row in df.iterrows():
    snippet = row.get("snippet", {})
    title = snippet.get("title", "Unknown Channel")
    st.markdown(f"- **{title}**")

# -------------------------------
# 🔐 Footer
# -------------------------------
st.markdown("""
    <p style='text-align: center; font-size: 13px;'>🔐 Secure & Private |
    <a href='https://www.youtufy.com/privacy' target='_blank'>Privacy Policy</a> |
    <a href='https://www.youtufy.com/terms' target='_blank'>Terms of Service</a> |
    <a href='https://www.youtufy.com/cookie' target='_blank'>Cookie Policy</a>
    </p>
""", unsafe_allow_html=True)
