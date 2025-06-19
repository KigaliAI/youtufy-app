# app/components/channel_card.py
import streamlit as st
import sys
def channel_card(channel_data):
    """Render a styled card for a YouTube channel."""

    snippet = channel_data.get("snippet", {})
    statistics = channel_data.get("statistics", {})

    title = snippet.get("title", "Unknown Channel")
    description = snippet.get("description", "No description available.")
    thumbnail = snippet.get("thumbnails", {}).get("default", {}).get("url", "https://via.placeholder.com/60")
    channel_id = snippet.get("resourceId", {}).get("channelId", "")
    subs = statistics.get("subscriberCount", "0")
    videos = statistics.get("videoCount", "0")

    youtube_url = f"https://www.youtube.com/channel/{channel_id}"

    # Show warning if channel ID is missing
    if not channel_id:
        st.warning("⚠️ Missing channel ID. Some data may be unavailable.")

    # Render HTML block
    st.markdown(f"""
    <div style='display: flex; align-items: center; margin-bottom: 1rem; border-bottom: 1px solid #ddd; padding-bottom: 1rem;'>
        <img src="{thumbnail}" alt="Channel Thumbnail" style="width: 60px; height: 60px; border-radius: 50%; margin-right: 15px;">
        <div>
            <h4 style="margin: 0;">
                <a href="{youtube_url}" target="_blank" style="color: rgb(112, 10, 160); text-decoration: none;">
                    {title}
                </a>
            </h4>
            <p style="margin: 0; font-size: 0.9rem;">📺 {videos} videos | 👥 {subs} subscribers</p>
            <p style="margin-top: 4px; font-size: 0.8rem; color: #444;">{description[:120]}...</p>
        </div>
    </div>
    """, unsafe_allow_html=True)
