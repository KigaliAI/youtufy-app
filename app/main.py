import streamlit as st
import pandas as pd
from datetime import datetime
from backend.auth import get_user_credentials
from backend.youtube import fetch_subscriptions
from app.components import channel_card

st.set_page_config(page_title="YouTufy", layout="wide")

# -------------------------------
# 👤 Check session (logged in?)
# -------------------------------
user_email = st.session_state.get("user")
username = st.session_state.get("username")

if user_email:
    st.title("📺 YouTufy – Your YouTube Subscriptions Dashboard")
    st.caption("🔒 Google OAuth Verified · Your data is protected")
    st.success(f"🎉 Welcome back, {username}!")

    with st.spinner("📡 Loading your YouTube subscriptions..."):
        creds = get_user_credentials(user_email)
        df = fetch_subscriptions(creds, user_email)

    if df.empty or 'statistics' not in df.columns or 'snippet' not in df.columns:
        st.warning("⚠️ No subscriptions found or data could not be fetched.")
        st.stop()

    # ✅ Safe numeric formatting
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
        if not isinstance(row.get("snippet"), dict):
            continue
        channel_card(row)

else:
    # -------------------------------
    # 🙋‍♀️ Not logged in? Prompt them
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