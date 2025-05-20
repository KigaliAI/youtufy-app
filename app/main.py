import os
import sys
import streamlit as st
import pandas as pd
from datetime import datetime
import time

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
    from backend.auth import get_user_credentials
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
# 🖼️ Display YouTufy Logo & Title
# -------------------------------
st.image("assets/logo.jpeg", width=60)  # ✅ Correct path after file move
st.title("YouTufy – YouTube Subscriptions App")
st.caption("🔒 Google OAuth Verified · Your data is protected")

# -------------------------------
# 👤 User session check
# -------------------------------
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
            df = fetch_subscriptions(creds, user_email)
            end_time = time.time()
            st.write(f"⏳ Subscriptions loaded in {end_time - start_time:.2f} seconds")  # Show execution time

        except Exception as e:
            st.error("❌ Failed to authenticate or retrieve subscriptions.")
            st.exception(e)
            st.stop()

    if df.empty or 'statistics' not in df.columns or 'snippet' not in df.columns:
        st.warning("⚠️ No subscriptions found or data could not be fetched.")
        st.stop()

    # ✅ Safe numeric conversions
    for col in ['statistics.subscriberCount', 'statistics.videoCount', 'statistics.viewCount']:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors='coerce')
        else:
            df[col] = 0

    df = df[df['snippet'].notna() & df['statistics'].notna()]

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

else:
    # -------------------------------
    # 🧭 Welcome screen (not logged in)
    # -------------------------------
    st.markdown("<h2 style='color:#ff00ff;'>Welcome to YouTufy!</h2>", unsafe_allow_html=True)
    st.image("assets/logo.jpeg", width=80)  # ✅ Larger logo for the welcome screen
    st.write("Organize and manage all your YouTube subscriptions in one place.")

    st.markdown("""
        <div style='background-color:#ff00ff; color:white; padding:10px; border-radius:5px;'>
            🔐 Sign in with Google to get started.
        </div>
    """, unsafe_allow_html=True)

    # ✅ Google OAuth Sign-In Button
    if st.button("🔐 Sign in with Google"):
        auth_url = generate_auth_url_for_user(user_email)
        st.markdown(f"[Click here to authenticate with Google]({auth_url})", unsafe_allow_html=True)

    st.markdown("---")

    # 🔎 Google OAuth Consent Screen Information
    st.markdown("""
        - ✅ **Google account selector must be shown**
        - ✅ **Requested scope: `youtube.readonly` must appear**
        - ✅ **User must click 'Allow'**
    """)

    st.markdown("---")

    # ✅ Privacy, Terms, & Cookie Policy Links
    st.markdown(
        """
        <p style='text-align: center; font-size: 13px;'>🔐 Secure & Private | 
        <a href='https://www.youtufy.com/privacy' target='_blank'>Privacy Policy</a> | 
        <a href='https://www.youtufy.com/terms' target='_blank'>Terms of Service</a> | 
        <a href='https://www.youtufy.com/cookie' target='_blank'>Cookie Policy</a>
        </p>
        """,
        unsafe_allow_html=True
    )
