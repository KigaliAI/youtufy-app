import streamlit as st
from backend.auth import get_user_credentials
import pandas as pd
from datetime import datetime
import time
from googleapiclient.discovery import build

st.set_page_config(page_title="YouTufy", layout="wide")

# -------------------------------
# ✅ Detect login
# -------------------------------
user_email = st.session_state.get("user")
username = st.session_state.get("username", "Guest")

if not user_email:
    st.warning("🔐 Please sign in to access your subscriptions.")

    st.markdown("""
    👉 <strong>Youtufy securely accesses your YouTube subscriptions</strong>.<br>
    🛡️ We request <code>youtube.readonly</code> permission.<br>
    ✅ Choose one of the login methods below:
    """, unsafe_allow_html=True)

    st.page_link("pages/login.py", label="Classic Login (Email & Password)", icon="✉️")
    st.page_link("pages/google_login.py", label="Sign in with Google", icon="🔐")
    st.stop()

# -------------------------------
# ✅ Logged-in user – show dashboard
# -------------------------------
st.success(f"✅ Welcome back, {username}!")

if st.button("🔄 Refresh Subscriptions"):
    st.cache_data.clear()
    st.rerun()

# ✅ Fetch credentials
creds = get_user_credentials(user_email)

# ✅ Fetch Subscriptions
@st.cache_data(ttl=600)
def fetch_subscriptions(creds, user_email=None):
    youtube = build("youtube", "v3", credentials=creds)
    subscriptions = []

    request = youtube.subscriptions().list(
        part="snippet,contentDetails",
        mine=True,
        maxResults=50
    )

    channel_ids = []

    while request:
        response = request.execute()
        items = response.get("items", [])
        subscriptions.extend(items)

        for item in items:
            cid = item["snippet"]["resourceId"]["channelId"]
            channel_ids.append(cid)

        request = youtube.subscriptions().list_next(request, response)

    # 🔄 Enrich with channel statistics
    enriched_data = []
    for i in range(0, len(channel_ids), 50):
        batch_ids = channel_ids[i:i+50]
        stats_response = youtube.channels().list(
            part="statistics",
            id=",".join(batch_ids)
        ).execute()

        stats_map = {item["id"]: item["statistics"] for item in stats_response.get("items", [])}

        for sub in subscriptions[i:i+50]:
            cid = sub["snippet"]["resourceId"]["channelId"]
            sub["statistics"] = stats_map.get(cid, {})

        enriched_data.extend(subscriptions[i:i+50])

    return pd.DataFrame(enriched_data)

with st.spinner("📡 Fetching subscriptions..."):
    try:
        df = fetch_subscriptions(creds)
    except Exception as e:
        st.error("❌ Failed to load subscriptions.")
        st.exception(e)
        st.stop()

if df.empty:
    st.warning("⚠️ No subscriptions found.")
else:
    st.metric("Total Channels", len(df))

    try:
        df["subscribers"] = pd.to_numeric(df["statistics"].apply(lambda s: s.get("subscriberCount", 0)), errors="coerce")
        df["videos"] = pd.to_numeric(df["statistics"].apply(lambda s: s.get("videoCount", 0)), errors="coerce")
        df["views"] = pd.to_numeric(df["statistics"].apply(lambda s: s.get("viewCount", 0)), errors="coerce")

        st.metric("Total Subscribers", f"{int(df['subscribers'].sum()):,}")
        st.metric("Total Videos", f"{int(df['videos'].sum()):,}")
    except Exception as e:
        st.warning("⚠️ Could not display metrics. Stats missing.")

    st.caption(f"📅 Last updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    for _, row in df.iterrows():
        title = row.get("snippet", {}).get("title", "Unknown")
        st.markdown(f"- **{title}**")
