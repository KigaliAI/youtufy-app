import streamlit as st
from backend.auth import get_user_credentials
from backend.youtube import fetch_subscriptions
from backend.favorites import get_favorites, add_favorite, remove_favorite
from datetime import datetime

st.set_page_config(page_title="My YouTufy", layout="wide")
st.title("🌟 My YouTufy – Favorite Channels")

user_email = st.session_state.get("user")
if not user_email:
    st.error("🔐 Please log in to view your dashboard.")
    st.stop()

with st.spinner("🔄 Loading your data..."):
    creds = get_user_credentials(user_email)
    df = fetch_subscriptions(creds, user_email)
    favorites = get_favorites(user_email)

if df.empty:
    st.warning("⚠️ No subscriptions found.")
    st.stop()

# Safe formatting
df['statistics.subscriberCount'] = pd.to_numeric(df['statistics.subscriberCount'], errors='coerce')
df['statistics.videoCount'] = pd.to_numeric(df['statistics.videoCount'], errors='coerce')
df['statistics.viewCount'] = pd.to_numeric(df['statistics.viewCount'], errors='coerce')

st.metric("Favorited Channels", len(favorites))
st.caption(f"⏰ Last updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

for _, row in df.iterrows():
    channel_id = row["id"]
    title = row["snippet"]["title"]
    st.markdown(f"### {title}")
    if channel_id in favorites:
        if st.button(f"💔 Unfavorite {title}", key=f"unfav-{channel_id}"):
            remove_favorite(user_email, channel_id)
            st.experimental_rerun()
    else:
        if st.button(f"⭐ Favorite {title}", key=f"fav-{channel_id}"):
            add_favorite(user_email, channel_id)
            st.experimental_rerun()

    st.markdown("---")
