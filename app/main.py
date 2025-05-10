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

# ✅ Import backend modules
try:
    from auth import get_user_credentials
    from youtube import fetch_subscriptions
except ModuleNotFoundError:
    st.error("❌ Failed to import backend modules.")
    st.stop()

# ✅ Import channel card
try:
    from utils.display import channel_card
except:
    def channel_card(row):
        st.write(f"📺 **{row.get('snippet', {}).get('title', 'Unknown Channel')}**")

# -------------------------------
# 👤 User session check
# -------------------------------
user_email = st.session_state.get("user")
username = st.session_state.get("username")

st.set_page_config(page_title="YouTufy", layout="wide")

if user_email:
    st.title("📺 YouTufy – Your YouTube Subscriptions Dashboard")
    st.caption("🔒 Google OAuth Verified · Your data is protected")

    # 🎉 Welcome message styled
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
        st.experimental_rerun()

    with st.spinner("📡 Loading your YouTube subscriptions..."):
        try:
            creds = get_user_credentials(user_email)
            df = fetch_subscriptions(creds, user_email)
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
    st.markdown("<h2 style='color:#ff00ff;'>Welcome to YouTufy!</h2>", unsafe_allow_html=True)
    st.write("Organize and manage all your YouTube subscriptions in one place.")
    st.markdown("""
        <div style='background-color:#ff00ff; color:white; padding:10px; border-radius:5px;'>
            🔐 Sign in or register to get started.
        </div>
    """, unsafe_allow_html=True)
    st.markdown("➡️ Use the sidebar to **[Register](/register)** or **[Login](/login)**.")
    st.markdown("---")
    st.markdown(
        "<p style='text-align: center; font-size: 13px;'>🔐 Secure & Private | "
        "<a href='https://kigaliai.github.io/YouTufy/privacy.html' target='_blank'>Privacy Policy</a> | "
        "<a href='https://kigaliai.github.io/YouTufy/terms.html' target='_blank'>Terms of Service</a></p>",
        unsafe_allow_html=True
    )
