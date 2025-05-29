# app/components/channel_card.py
import streamlit as st

def channel_card(row):
    snippet = row["snippet"]
    statistics = row["statistics"]

    channel_title = snippet.get("title", "Unknown Channel")
    channel_id = row.get("id", {}).get("channelId") or row.get("id")
    channel_url = f"https://www.youtube.com/channel/{channel_id}"
    thumbnail = snippet.get("thumbnails", {}).get("default", {}).get("url", "")

    with st.container():
        st.markdown(f"""
            <div style='border: 1px solid #ccc; border-radius: 10px; padding: 15px; margin-bottom: 15px; background: #fafafa;'>
                <div style='display: flex; align-items: center;'>
                    <img src="{thumbnail}" alt="Thumbnail" style="width: 80px; height: 80px; margin-right: 15px; border-radius: 8px;" />
                    <div>
                        <h3 style="margin: 0;">
                            <a href="{channel_url}" target="_blank" style="text-decoration: none; color: magenta;">
                                {channel_title}
                            </a>
                        </h3>
                        <p style="margin: 5px 0 0; font-size: 0.9rem;">
                            📊 {int(statistics.get("subscriberCount", 0)):,} subscribers · 🎬 {int(statistics.get("videoCount", 0)):,} videos
                        </p>
                    </div>
                </div>
            </div>
        """, unsafe_allow_html=True)
