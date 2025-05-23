import streamlit as st
import pandas as pd
from datetime import datetime
from backend.youtube import fetch_subscriptions_sync
from backend.auth import get_user_credentials

st.set_page_config(page_title="📺 All My YouTube Subscriptions", layout="wide")
st.title("📺 All My YouTube Subscriptions")

# ✅ Ensure user is authenticated
if not st.session_state.get("oauth_token"):
    st.error("🔐 You need to sign in first!")
    st.switch_page("pages/google_login.py")
    st.stop()

# ✅ Fetch credentials safely
creds = get_user_credentials()
if not creds:
    st.error("❌ Failed to authenticate. Please sign in again.")
    st.switch_page("pages/login.py")
    st.stop()

# ✅ Load subscriptions
st.write("🔄 Fetching your YouTube subscriptions...")
df = fetch_subscriptions_sync()

if df.empty or "snippet" not in df.columns or "statistics" not in df.columns:
    st.warning("⚠️ No subscriptions found or data missing.")
    st.stop()

# ✅ Convert statistics to numeric values
for col in ["statistics.subscriberCount", "statistics.videoCount", "statistics.viewCount"]:
    if col in df.columns:
        df[col] = pd.to_numeric(df[col], errors="coerce")
    else:
        df[col] = 0

# ✅ Display overall metrics
st.metric("Total Channels", len(df))
st.metric("Total Subscribers", f"{int(df['statistics.subscriberCount'].sum()):,}")
st.metric("Total Videos", f"{int(df['statistics.videoCount'].sum()):,}")
st.caption(f"📅 Last updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

st.markdown("---")

# ✅ Display subscription details
for _, row in df.iterrows():
    if not isinstance(row.get("snippet"), dict):
        continue
    channel_card(row)  # ✅ Display each channel using `channel_card()`
