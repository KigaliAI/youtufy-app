import os
import sys
import streamlit as st
import pandas as pd
from datetime import datetime

# -------------------------------
# ✅ Adjust backend import path
# -------------------------------
backend_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "backend"))
sys.path.insert(0, backend_path)

# -------------------------------
# ✅ Import backend modules
# -------------------------------
try:
    from auth import get_user_credentials
    from youtube import fetch_subscriptions
except ModuleNotFoundError as e:
    st.error("❌ Failed to import backend modules.")
    st.stop()

# 🔧 Optional: try to import channel_card if it's defined in a utility
try:
    from utils.display import channel_card  # adjust path if needed
except:
    def channel_card(row):
        st.write(f"📺 **{row.get('snippet', {}).get('title', 'Unknown Channel')}**")

# -------------------------------
# 👤 User session check
# -------------------------------
user_email = st.session_state.get("user")
username = st.session_state.get("username")

if user_email:
    st.title("📺 YouTufy – Your YouTube Subscriptions Dashboard")
    st.caption("🔒 Google OAuth Verified · Your data is protected")
    st.success(f"🎉 Welcome back, {username}!")

    # 🔁 Optional: refresh button
    if st.button("🔄 Refresh Subscriptions"):
        st.cache_data.clear()

    with st.spinner("📡 Loading your YouTube subscriptions..."):
        try:
            creds = get_user_credentials(user_email)
            df = fetch_subscriptions(creds, user_email)
        except Exception as e:
            st.error("❌ Failed to authenticate or retrieve subscriptions.")
            st.exception(e)
            st.stop()

    # Validate data
    if df.empty or 'statistics' not in df.columns or 'snippet' not in df.columns:
        st.warning("⚠️ No subscriptions found or data could not be fetched.")
        st.stop()

    # Format stats safely
    for col in ['statistics.subscriberCount', 'statistics.videoCount', 'statistics.viewCount']:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors='coerce')
        else:
            df[col] = 0

    df = df[df['snippet'].notna() & df['statistics'].notna()]

    # Dashboard metrics
    st.metric("Total Channels", len(df))
    st.metric("Total Subscribers", f"{int(df['statistics.subscriberCount'].sum()):,}")
    st.metric("Total Videos", f"{int(df['statistics.videoCount'].sum()):,}")
    st.caption(f"📅 Last updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

    st.markdown("---")

    for _, row in df.iterrows():
        if not isinstance(row.get("snippet"), dict):
            continue
        channel_card(row)

else:
    # -------------------------------
    # 🧭 Welcome screen (not logged in)
    # -------------------------------
    st.title("📺 YouTufy – Your YouTube Subscriptions Dashboard")
    st.caption("🔒 Google OAuth Verified · Your data is protected")
    st.markdown("Welcome to **YouTufy**!")
    st.write("Organize and manage all your YouTube subscriptions in one place.")
    st.info("🔐 Sign in or register to get started.")
    st.markdown("➡️ Use the sidebar to **[Register](/register)** or **[Login](/login)**.")
    st.markdown("---")
    st.markdown(
        "<p style='text-align: center; font-size: 13px;'>🔐 Secure & Private | "
        "<a href='https://kigaliai.github.io/YouTufy/privacy.html' target='_blank'>Privacy Policy</a> | "
        "<a href='https://kigaliai.github.io/YouTufy/terms.html' target='_blank'>Terms of Service</a></p>",
        unsafe_allow_html=True
    )
