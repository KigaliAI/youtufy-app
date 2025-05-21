import streamlit as st
from google_auth_oauthlib.flow import InstalledAppFlow
import logging

# 🔐 Google OAuth Configuration
SCOPES = ['https://www.googleapis.com/auth/youtube.readonly']

def login_google():
    """Handles Google authentication."""
    secret_path = "config/client_secret.json"  # ✅ Ensure this path exists!

    flow = InstalledAppFlow.from_client_secrets_file(
        secret_path, SCOPES, include_granted_scopes=True
    )

    auth_url, _ = flow.authorization_url(prompt='consent', access_type='offline')

    # ✅ Display the login button
    st.markdown(f"🔗 **[Sign in with Google]({auth_url})**", unsafe_allow_html=True)
    logging.info(f"🔗 Generated Google Login URL: {auth_url}")

# ✅ Page Setup
st.set_page_config(page_title="Google Login", layout="centered")
st.title("🔐 Sign in to YouTufy with Google")

st.markdown("""
    🎥 **Youtufy securely accesses your YouTube subscriptions**.<br>
    🛡️ We request **youtube.readonly** permission to display your subscribed channels.<br>
    ✅ Click **Sign in with Google** to grant access and manage your subscriptions easily.
""", unsafe_allow_html=True)

# 🏆 Run Google Authentication
login_google()
