# app/pages/google_login.py
import backend.oauth
print("🔍 Available functions:", dir(backend.oauth))

import os
import sys
import streamlit as st
import pandas as pd
from datetime import datetime
from dotenv import load_dotenv

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../backend")))
print("🔍 Python Path:", sys.path)
from backend.oauth import (
    get_credentials_from_code,
    get_flow, get_auth_flow,
    refresh_credentials,
    store_oauth_credentials
)
from backend.youtube import fetch_subscriptions
from app.components import channel_card

# ✅ Load environment variables
load_dotenv()
REDIRECT_URI = os.getenv("OAUTH_REDIRECT_URI", "https://youtufy-one.streamlit.app/google_login")

# ✅ Configure Streamlit page
st.set_page_config(page_title="YouTufy – Dashboard", layout="wide")
st.title("🌍 Sign in with Google")

# ✅ Session state
user_email = st.session_state.get("user")
username = st.session_state.get("username")
authenticated = st.session_state.get("authenticated", False)
google_creds_json = st.session_state.get("google_creds")

# 🔄 Handle Google OAuth callback with code
if "code" in st.query_params and not authenticated:
    st.info("🔁 Exchanging code for tokens...")
    try:
        code = st.query_params["code"]
        creds = get_credentials_from_code(code, REDIRECT_URI)

        user_email = creds.id_token.get("email")
        if not user_email:
            st.error("❌ Google login failed: No email found.")
            st.stop()

        # ✅ Save session state
        st.session_state["user"] = user_email
        st.session_state["username"] = user_email.split("@")[0]
        st.session_state["google_creds"] = creds.to_json()
        st.session_state["authenticated"] = True

        # ✅ Store credentials on disk (if needed)
        store_oauth_credentials(creds, user_email)

        st.success("✅ Login successful! Redirecting...")
        st.rerun()

    except Exception as e:
        st.error("❌ Google OAuth failed.")
        st.exception(e)
        st.stop()

# 🚪 Not authenticated → show Google login button
if not authenticated:
    flow = get_flow(REDIRECT_URI)
    auth_url, _ = flow.authorization_url(prompt="consent", access_type="offline")

    st.markdown(f"""
        <div style="text-align: center; margin-top: 30px;">
            <a href="{auth_url}" style="
                background-color: #8F00FF;
                color: white;
                padding: 16px 28px;
                border-radius: 8px;
                text-decoration: none;
                font-weight: bold;
                font-size: 1.2rem;">
                🔐 Sign in with Google
            </a>
        </div>
    """, unsafe_allow_html=True)
    st.stop()

# ✅ Authenticated – fetch subscriptions and show dashboard
st.markdown("<h1 style='font-size:1.8rem; font-weight:bold; color:magenta;'>YouTufy – Your YouTube Subscriptions Dashboard</h1>", unsafe_allow_html=True)
st.caption("🔒 Google OAuth Verified · Your data is protected")
st.success(f"🎉 Welcome back, {username.capitalize()}!")

# 🔄 Refresh credentials if needed
creds = refresh_credentials(google_creds_json)
st.session_state["google_creds"] = creds.to_json()

# 📡 Fetch subscriptions
with st.spinner("📡 Loading your YouTube subscriptions..."):
    df = fetch_subscriptions(creds, user_email)

# ✅ Validate response
if df.empty or 'statistics' not in df.columns or 'snippet' not in df.columns:
    st.warning("⚠️ No subscriptions found.")
    st.stop()

# 🔧 Normalize numeric values
for col in ['statistics.subscriberCount', 'statistics.videoCount', 'statistics.viewCount']:
    df[col] = pd.to_numeric(df.get(col, pd.Series(0)), errors='coerce')

# 📈 Summary metrics
st.metric("Total Channels", len(df))
st.metric("Total Subscribers", f"{int(df['statistics.subscriberCount'].sum()):,}")
st.metric("Total Videos", f"{int(df['statistics.videoCount'].sum()):,}")
st.caption(f"📅 Last updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

st.markdown("---")

# 🧾 Show channel cards
for _, row in df.iterrows():
    if isinstance(row.get("snippet"), dict):
        channel_card(row)
