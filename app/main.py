import os
import sys
import streamlit as st
import pandas as pd
from datetime import datetime
import time
from googleapiclient.discovery import build

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
    from backend.auth import get_user_credentials, generate_auth_url_for_user  # ✅ Fixed missing function import
    from backend.youtube import fetch_subscriptions
except ModuleNotFoundError:
    st.error("❌ Failed to import backend modules.")
    st.stop()

# ✅ Import utilities
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "utils")))
try:
    from utils.display import channel_card
except ModuleNotFoundError:
    def channel_card(row):
        logo_path = "assets/logo.jpeg"

        if os.path.exists(logo_path):
            st.image(logo_path, width=20)  # ✅ Small YouTufy logo instead of 📺
            st.write(f"**{row.get('snippet', {}).get('title', 'Unknown Channel')}**")
        else:
            st.write(f"**{row.get('snippet', {}).get('title', 'Unknown Channel')}**")

# -------------------------------
# 📡 Optimized Fetch Subscriptions
# -------------------------------
@st.cache_data(ttl=600)  # ✅ Cache API data for 10 minutes
def fetch_subscriptions_cached(creds):
    youtube = build("youtube", "v3", credentials=creds)

    subscriptions = []
    request = youtube.subscriptions().list(
        part="snippet,contentDetails",
        mine=True,
        maxResults=50  # ✅ Load only 50 channels at a time for better speed
    )

    while request:
        response = request.execute()
        subscriptions.extend(response.get("items", []))
        request = youtube.subscriptions().list_next(request, response)

    return pd.DataFrame(subscriptions)

# -------------------------------
# 🖼️ Logo & Title (Improved UI)
# -------------------------------
col1, col2 = st.columns([1, 3])  # ✅ Organize layout
with col1:
    st.image("assets/logo.jpeg", width=60)  # ✅ Keep only one logo, left-aligned

with col2:
    st.markdown("<h1 style='margin-top: 10px;'>YouTufy – YouTube Subscriptions App</h1>", unsafe_allow_html=True)
    st.caption("🔒 Google OAuth Verified · Your data is protected")

# 🏷️ Welcome Message
st.markdown("<h2 style='color:#ff00ff;'>Welcome to YouTufy!</h2>", unsafe_allow_html=True)

# 🛠️ Improved OAuth Explanation
st.markdown("""
    <div style='background-color:#f0f0f0; padding:15px; border-radius:6px; font-size:16px;'>
        🎥 **Youtufy securely accesses your YouTube subscriptions**.<br>
        🛡️ We request **youtube.readonly** permission to display your subscribed channels.<br>
        ✅ Click **Sign in with Google** to grant access and manage your subscriptions easily.
    </div>
""", unsafe_allow_html=True)

# 🔐 Sign-in Button (Fixed `generate_auth_url_for_user`)
if st.button("🔐 Sign in with Google"):
    user_email = st.session_state.get("user")  # ✅ Ensure user email exists
    if user_email:
        auth_url = generate_auth_url_for_user(user_email)
        st.markdown(f"[Click here to authenticate with Google]({auth_url})", unsafe_allow_html=True)
    else:
        st.error("❌ No user session found. Please try refreshing the page.")

st.markdown("---")

# 👤 User session check
user_email = st.session_state.get("user")
username = st.session_state.get("username")

if user_email:
    st.markdown(
        f"""
        <div style="background-color:#ff00ff; color:white; padding:12px 20px; border-radius:6px; font-weight:bold;">
            🎉 Welcome back, {username}!
        </div>
        """,
        unsafe_allow_html=True
    )

    # 🔁 Refresh button
    if st.button("🔄 Refresh Subscriptions"):
        st.cache_data.clear()
        st.rerun()

    # 📡 Load subscriptions with optimized error handling
    with st.spinner("📡 Loading your YouTube subscriptions..."):
        try:
            creds = get_user_credentials(user_email)

            # ✅ Debug: Measure API call time
            start_time = time.time()
            df = fetch_subscriptions_cached(creds)
            end_time = time.time()
            st.write(f"⏳ Subscriptions loaded in {end_time - start_time:.2f} seconds")  # Show execution time

        except Exception as e:
            st.error("❌ Failed to authenticate or retrieve subscriptions.")
            st.exception(e)
            st.stop()

    if df.empty or 'snippet' not in df.columns:
        st.warning("⚠️ No subscriptions found or data could not be fetched.")
        st.stop()

    # ✅ Safe numeric conversions
    numeric_columns = ['statistics.subscriberCount', 'statistics.videoCount', 'statistics.viewCount']
    for col in numeric_columns:
        df[col] = pd.to_numeric(df.get(col, 0), errors="coerce")

    # 📊 Dashboard metrics
    st.metric("Total Channels", len(df))
    st.metric("Total Subscribers", f"{int(df['statistics.subscriberCount'].sum()):,}")
    st.metric("Total Videos", f"{int(df['statistics.videoCount'].sum()):,}")
    st.caption(f"📅 Last updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

    st.markdown("---")

    # 🖼️ Display channels using `channel_card`
    for _, row in df.iterrows():
        if isinstance(row.get("snippet"), dict):
            channel_card(row)

# ✅ Privacy, Terms, & Cookie Policy Links
st.markdown("""
    <p style='text-align: center; font-size: 13px;'>🔐 Secure & Private | 
    <a href='https://www.youtufy.com/privacy' target='_blank'>Privacy Policy</a> | 
    <a href='https://www.youtufy.com/terms' target='_blank'>Terms of Service</a> | 
    <a href='https://www.youtufy.com/cookie' target='_blank'>Cookie Policy</a>
    </p>
""", unsafe_allow_html=True)
