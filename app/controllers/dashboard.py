# app/controllers/dashboard.py

import os
import sys
import pandas as pd
from datetime import datetime
import streamlit as st

# Ensure import paths are correct for backend modules
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../")))

from backend.oauth import get_user_credentials
from backend.youtube import fetch_subscriptions

def load_dashboard(user_email, username):
    """Render the YouTufy dashboard for the authenticated user."""
    st.markdown(
        "<h1 style='font-size:1.8rem; font-weight:bold; color:rgb(112, 10, 160);'>YouTufy – Your YouTube Subscriptions System</h1>",
        unsafe_allow_html=True
    )
    st.caption("🔒 Your data is protected · Access granted via Google OAuth (`youtube.readonly`)")
    st.success(f"🎉 Welcome back, {username.capitalize()}!")

    # 🔄 Fetch YouTube data
    with st.spinner("📡 Loading your YouTube subscriptions..."):
        try:
            creds = get_user_credentials(user_email)
            df = fetch_subscriptions(creds, user_email)
        except Exception as e:
            st.error(f"⚠️ Failed to retrieve subscriptions: {e}")
            st.stop()

    # 🧪 Validate fetched data
    if df.empty or not {"statistics", "snippet"}.issubset(df.columns):
        st.warning("⚠️ No valid YouTube subscription data found.")
        st.stop()

    # 🔢 Normalize statistics
    numeric_cols = ["statistics.subscriberCount", "statistics.videoCount", "statistics.viewCount"]
    for col in numeric_cols:
        df[col] = pd.to_numeric(df.get(col, pd.Series(0)), errors="coerce").fillna(0)

    df = df[df["snippet"].notna() & df["statistics"].notna()]

    # 📊 Display key metrics
    st.metric("Total Channels", len(df))
    st.metric("Total Subscribers", f"{int(df['statistics.subscriberCount'].sum()):,}")
    st.metric("Total Videos", f"{int(df['statistics.videoCount'].sum()):,}")
    st.caption(f"📅 Last updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

    st.markdown("---")

    # 🔽 Display individual channel cards
    for _, row in df.iterrows():
        snippet = row.get("snippet", {})
        stats = row.get("statistics", {})
        title = snippet.get("title", "Unknown Channel")
        channel_url = row.get("channelUrl", "")
        subs = int(stats.get("subscriberCount", 0))
        videos = int(stats.get("videoCount", 0))
        latest = row.get("latestVideoDate", "N/A")

        # 🔗 Clickable channel badge
        if channel_url:
            st.markdown(
                f"""<a href="{channel_url}" target="_blank" style="text-decoration:none;">
                    <div style="background-color:#8F00FF;padding:10px 15px;border-radius:6px;display:inline-block;margin-bottom:5px;">
                        <span style="color:white;font-weight:bold;">📺 {title}</span>
                    </div>
                </a>""",
                unsafe_allow_html=True
            )
        else:
            st.subheader(title)

        st.write(f"👥 Subscribers: {subs:,}")
        st.write(f"🎞️ Videos: {videos:,}")
        st.write(f"📅 Latest Video: {latest}")
        st.markdown("---")
