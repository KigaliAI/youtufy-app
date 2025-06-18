# app/pages/dashboard.py
import sys
import os
import json
import streamlit as st
import pandas as pd
from datetime import datetime

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

from backend.oauth import get_flow, get_credentials_from_code, refresh_credentials
from backend.auth import store_oauth_credentials
from backend.youtube import fetch_subscriptions
from app.components.channel_card import channel_card

# ✅ Redirect URI (not used directly, just for clarity)
REDIRECT_URI = "https://youtufy-one.streamlit.app/pages/dashboard.py"

# ✅ Configure Page
st.set_page_config(page_title="YouTufy – Dashboard", layout="wide")

# 🔐 Session & OAuth Handling
user_email = st.session_state.get("user", None)
username = st.session_state.get("username", None)
google_creds_json = st.session_state.get("google_creds", None)
authenticated = st.session_state.get("authenticated", False)
creds = None

# 🔄 Refresh credentials if stored
if user_email and google_creds_json:
    creds = refresh_credentials(google_creds_json)
    st.session_state["google_creds"] = creds.to_json()
    st.session_state["authenticated"] = True

# 🔄 Handle Google OAuth Callback
elif st.query_params.get("code") and not authenticated:
    st.info("🔁 Exchanging authorization code for tokens...")
    try:
        code = st.query_params["code"]
        creds = get_credentials_from_code(code, REDIRECT_URI)

        user_email = creds.id_token.get("email")
        if not user_email:
            st.error("❌ Google login failed: No email found.")
            st.stop()

        # Save session credentials
        st.session_state["user"] = user_email
        st.session_state["username"] = user_email.split("@")[0]
        st.session_state["google_creds"] = creds.to_json()
        st.session_state["authenticated"] = True

        # Persist credentials
        store_oauth_credentials(creds, user_email)

        st.success(f"✅ Logged in as {user_email}. Reloading...")
        st.rerun()

    except Exception as e:
        st.error("❌ Google OAuth token exchange failed.")
        st.exception(e)
        st.stop()

# 🔑 Not authenticated → Show Google Login Prompt
if not st.session_state.get("authenticated", False):
    flow = get_flow(REDIRECT_URI)
    auth_url, _ = flow.authorization_url(prompt="consent", access_type="offline")

    st.markdown(f"""
        <p style="text-align:center; margin-top: 40px;">
            <a href="{auth_url}" style="
                padding: 14px 24px;
                background-color: #8F00FF;
                color: white;
                text-decoration: none;
                border-radius: 6px;
                font-weight: bold;
                font-size: 1rem;">
                🔐 Sign in with Google
            </a>
        </p>
    """, unsafe_allow_html=True)
    st.stop()

# ✅ Authenticated UI
st.markdown("<h1 style='font-size:1.8rem; font-weight:bold; color:magenta;'>YouTufy – Your YouTube Subscriptions Dashboard</h1>", unsafe_allow_html=True)
st.caption("🔒 Google OAuth Verified · Your data is protected")
st.success(f"🎉 Welcome back, {st.session_state.username.capitalize()}!")

# 📡 Fetch YouTube subscriptions
with st.spinner("📡 Loading your YouTube subscriptions..."):
    df = fetch_subscriptions(creds, user_email)

# ✅ Validate and clean data
if df.empty or "snippet" not in df.columns or "statistics" not in df.columns:
    st.warning("⚠️ No subscriptions found or API returned invalid data.")
    st.stop()

for col in ["statistics.subscriberCount", "statistics.videoCount", "statistics.viewCount"]:
    df[col] = pd.to_numeric(df.get(col, pd.Series(0)), errors="coerce").fillna(0)

# 📊 Metrics
st.metric("Total Channels", len(df))
st.metric("Total Subscribers", f"{int(df['statistics.subscriberCount'].sum()):,}")
st.metric("Total Videos", f"{int(df['statistics.videoCount'].sum()):,}")
st.caption(f"📅 Last updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

st.markdown("---")

# 🖥️ Render each channel using channel_card
for _, row in df.iterrows():
    if isinstance(row.get("snippet"), dict):
        channel_card(row)
