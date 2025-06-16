#app/pages/google_login.py
import os
import streamlit as st
import pandas as pd
from datetime import datetime
from dotenv import load_dotenv

from backend.oauth import (
    get_user_credentials,
    store_oauth_credentials,
    get_flow,
    get_credentials_from_code,
    refresh_credentials
)
from backend.youtube import fetch_subscriptions
from app.components import channel_card

# ✅ Load environment variables
load_dotenv()
REDIRECT_URI = os.getenv("OAUTH_REDIRECT_URI", "https://youtufy-one.streamlit.app/google_login")

# ✅ Configure Page
st.set_page_config(page_title="YouTufy – Dashboard", layout="wide")
st.title("🌍 Sign in with Google")

# 🔐 Session State Variables
user_email = st.session_state.get("user", None)
username = st.session_state.get("username", None)
google_creds_json = st.session_state.get("google_creds", None)
authenticated = st.session_state.get("authenticated", False)
creds = None

# 🔄 Handle Google OAuth Callback (?code=...)
if "code" in st.query_params and not authenticated:
    st.info("🔁 Exchanging authorization code for tokens...")
    try:
        code = st.query_params["code"]
        creds = get_credentials_from_code(code, REDIRECT_URI)

        user_email = creds.id_token.get("email", None)
        if not user_email:
            st.error("❌ Google login failed: No email found.")
            st.stop()

        # ✅ Save session credentials
        st.session_state["user"] = user_email
        st.session_state["username"] = user_email.split("@")[0]
        st.session_state["google_creds"] = creds.to_json()
        st.session_state["authenticated"] = True

        # ✅ Store credentials securely
        store_oauth_credentials(creds, user_email)

        st.success("✅ Login successful. Redirecting to dashboard...")
        st.switch_page("dashboard")

    except Exception as e:
        st.error("❌ Google OAuth token exchange failed.")
        st.exception(e)
        st.stop()

# 🔑 Not authenticated → Show Google Login Prompt
if not authenticated:
    flow = get_flow(REDIRECT_URI)
    auth_url, _ = flow.authorization_url(prompt="consent", access_type="offline")

    st.markdown(f"""
        <p style="text-align:center; margin-top: 20px;">
            <a href="{auth_url}" style="
                padding: 14px 24px;
                background-color: #8F00FF;
                color: white;
                text-decoration: none;
                border-radius: 6px;
                font-weight: bold;">
                🔐 Sign in with Google
            </a>
        </p>
    """, unsafe_allow_html=True)
    st.stop()

# ✅ Authenticated User – Load Dashboard
st.markdown("<h1 style='font-size:1.8rem; font-weight:bold; color:magenta;'>YouTufy – Your YouTube Subscriptions Dashboard</h1>", unsafe_allow_html=True)
st.caption("🔒 Google OAuth Verified · Your data is protected")
st.success(f"🎉 Welcome back, {st.session_state.username.capitalize()}!")

# 🔄 Refresh Credentials If Expired
creds = refresh_credentials(st.session_state.get("google_creds"))
st.session_state["google_creds"] = creds.to_json()

# 📡 Fetch YouTube Subscriptions
with st.spinner("📡 Loading your YouTube subscriptions..."):
    df = fetch_subscriptions(creds, user_email)

# ✅ Validate Subscription Data
if df.empty or 'statistics' not in df.columns or 'snippet' not in df.columns:
    st.warning("⚠️ No subscriptions found.")
    st.stop()

# 🔄 Normalize Numerical Values
for col in ['statistics.subscriberCount', 'statistics.videoCount', 'statistics.viewCount']:
    df[col] = pd.to_numeric(df.get(col, pd.Series(0)), errors='coerce')

# 📊 Display Key Subscription Metrics
st.metric("Total Channels", len(df))
st.metric("Total Subscribers", f"{int(df['statistics.subscriberCount'].sum()):,}")
st.metric("Total Videos", f"{int(df['statistics.videoCount'].sum()):,}")
st.caption(f"📅 Last updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

st.markdown("---")

# 🖥️ Render YouTube Subscription Cards
for _, row in df.iterrows():
    if isinstance(row.get("snippet"), dict):
        channel_card(row)

