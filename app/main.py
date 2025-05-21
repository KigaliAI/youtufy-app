import os
import sys
import streamlit as st
import pandas as pd
from datetime import datetime
import time
from googleapiclient.discovery import build

# -------------------------------
# ✅ Page config
# -------------------------------
st.set_page_config(page_title="YouTufy", layout="wide")

# -------------------------------
# ✅ Backend imports
# -------------------------------
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "backend")))
try:
    from backend.auth import get_user_credentials
except ModuleNotFoundError:
    st.error("❌ Failed to load backend modules.")
    st.stop()

# -------------------------------
# ✅ Check user login status
# -------------------------------
user_email = st.session_state.get("user")
username = st.session_state.get("username", "Guest")

# -------------------------------
# 🖼️ Welcome Screen (unauthenticated users)
# -------------------------------
if not user_email:
    # UI only — no subscriptions, no session
    col1, col2 = st.columns([1, 3])
    with col1:
        st.image("assets/logo.jpeg", width=60)

    with col2:
        st.markdown("<h1 style='margin-top: 10px;'>YouTufy – YouTube Subscriptions App</h1>", unsafe_allow_html=True)
        st.caption("🔒 Google OAuth Verified · Your data is protected")

    st.markdown("<h2 style='color:#ff00ff;'>Welcome to YouTufy!</h2>", unsafe_allow_html=True)

    st.markdown("""
        <div style='background-color:#f0f0f0; padding:15px; border-radius:6px; font-size:16px;'>
            👉 <strong>Youtufy securely accesses your YouTube subscriptions</strong>.<br>
            👉 We request <code>youtube.readonly</code> permission only.<br>
            👉 Click below to sign in with Google and get started.
        </div>
    """, unsafe_allow_html=True)

    # Redirect to login.py
    if st.button("🔐 Sign in with Google"):
        st.switch_page("pages/login.py")

    st.stop()  # Stop here if not logged in

# -------------------------------
# ✅ Authenticated User: Dashboard
# -------------------------------
col1, col2 = st.columns([1, 3])
with col1:
    st.image("assets/logo.jpeg", width=60)
with col2:
    st.markdown("<h1 style='margin-top: 10px;'>YouTufy – YouTube Subscriptions App</h1>", unsafe_allow_html=True)
    st.caption("🔒 Google OAuth Verified")

st.success(f"🎉 Welcome back, {username}!")

# -------------------------------
# 📡 Fetch Subscriptions
# -------------------------------
@st.cache_data(ttl=600)
def fetch_subscriptions(creds):
    youtube = build("youtube", "v3", credentials=creds)
    subscriptions = []

    request = youtube.subscriptions().list(
        part="snippet,contentDetails",
        mine=True,
        maxResults=50
    )

    while request:
        response = request.execute()
        subscriptions.extend(response.get("items", []))
        request = youtube.subscriptions().list_next(request, response)

    return pd.DataFrame(subscriptions)

# -------------------------------
# 🔁 Refresh + Load
# -------------------------------
if st.button("🔄 Refresh Subscriptions"):
    st.cache_data.clear()
    st.rerun()

creds = get_user_credentials(user_email)

with st.spinner("📡 Loading your subscriptions..."):
    try:
        start = time.time()
        df = fetch_subscriptions(creds)
        st.write(f"⏳ Loaded in {time.time() - start:.2f} seconds")
    except Exception as e:
        st.error("❌ Failed to load subscriptions.")
        st.exception(e)
        st.stop()

if df.empty:
    st.warning("⚠️ No subscriptions found.")
    st.stop()

st.metric("Total Channels", len(df))

# -------------------------------
# 🖼️ Show channels
# -------------------------------
for _, row in df.iterrows():
    title = row.get("snippet", {}).get("title", "Unknown")
    st.markdown(f"- **{title}**")

st.markdown("""
    <p style='text-align: center; font-size: 13px;'>🔐 Secure & Private |
    <a href='https://www.youtufy.com/privacy' target='_blank'>Privacy Policy</a> |
    <a href='https://www.youtufy.com/terms' target='_blank'>Terms of Service</a> |
    <a href='https://www.youtufy.com/cookie' target='_blank'>Cookie Policy</a>
    </p>
""", unsafe_allow_html=True)
