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
def fetch_subscriptions(creds):
    youtube = build("youtube", "v3", credentials=creds)
    subs = []
    req = youtube.subscriptions().list(part="snippet", mine=True, maxResults=50)
    while req:
        res = req.execute()
        subs.extend(res.get("items", []))
        req = youtube.subscriptions().list_next(req, res)
    return pd.DataFrame(subs)

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
    st.caption(f"📅 Last updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    for _, row in df.iterrows():
        st.markdown(f"- **{row['snippet']['title']}**")
