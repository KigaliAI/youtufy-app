import streamlit as st
import pandas as pd
from datetime import datetime

# Import backend
from backend.auth import get_user_credentials
from backend.youtube import fetch_subscriptions
from backend.favorites import get_favorites, add_favorite, remove_favorite

# Page config
st.set_page_config(page_title="My YouTufy", layout="wide")
st.title("🌟 My YouTufy – Favorite Channels")

# -------------------------------
# 👤 Check user login
# -------------------------------
user_email = st.session_state.get("user")
if not user_email:
    st.error("🔐 Please log in to view your dashboard.")
    st.stop()

# -------------------------------
# 📡 Load data
# -------------------------------
with st.spinner("🔄 Loading your data..."):
    try:
        creds = get_user_credentials(user_email)
        df = fetch_subscriptions(creds, user_email)
        favorites = get_favorites(user_email)
    except Exception as e:
        st.error("❌ Failed to load your data.")
        st.exception(e)
        st.stop()

if df.empty:
    st.warning("⚠️ No subscriptions found.")
    st.stop()

# -------------------------------
# ✅ Format and clean data
# -------------------------------
for col in ['statistics.subscriberCount', 'statistics.videoCount', 'statistics.viewCount']:
    if col in df.columns:
        df[col] = pd.to_numeric(df[col], errors='coerce')
    else:
        df[col] = 0

df = df[df['snippet'].notna() & df['statistics'].notna()]

# -------------------------------
# 📊 Header metrics
# -------------------------------
st.metric("Favorited Channels", len(favorites))
st.caption(f"⏰ Last updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
st.markdown("---")

# -------------------------------
# ⭐ Display channels
# -------------------------------
favorited_any = False

for _, row in df.iterrows():
    channel_id = row.get("id")
    snippet = row.get("snippet", {})
    title = snippet.get("title", "Unknown Channel")

    with st.container():
        st.markdown(f"### {title}")

        if channel_id in favorites:
            favorited_any = True
            if st.button(f"💔 Unfavorite", key=f"unfav-{channel_id}"):
                remove_favorite(user_email, channel_id)
                st.success(f"Removed {title} from favorites.")
                st.experimental_rerun()
        else:
            if st.button(f"⭐ Favorite", key=f"fav-{channel_id}"):
                add_favorite(user_email, channel_id)
                st.success(f"Added {title} to favorites.")
                st.experimental_rerun()

        st.markdown("---")

# -------------------------------
# 🧾 Empty state message
# -------------------------------
if not favorited_any:
    st.info("You haven’t favorited any channels yet. ⭐ Use the buttons above to start!")
