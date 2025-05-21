import os
import tempfile
import streamlit as st
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
import logging

# ----------------------------------
# 🔐 SCOPES & REDIRECT URI
# ----------------------------------
SCOPES = ['https://www.googleapis.com/auth/youtube.readonly']
REDIRECT_URI = st.secrets.get("OAUTH_REDIRECT_URI", "http://localhost:8501/")

# ----------------------------------
# 🔑 Generate OAuth login URL (Fix: Make `user_email` Optional)
# ----------------------------------
def generate_auth_url_for_user(user_email=None):
    """Always return authentication URL to allow Google login."""
    secret_path = _get_cached_secret_path()
    flow = InstalledAppFlow.from_client_secrets_file(secret_path, SCOPES)
    
    auth_url, _ = flow.authorization_url(prompt='consent', access_type='offline')

    return auth_url  # ✅ Redirects user to Google's authentication page

# ✅ Fix: `user_email` is now optional to prevent login errors

# ----------------------------------
# 🔑 Retrieve or refresh user credentials
# ----------------------------------
def get_user_credentials(user_email):
    """Loads, refreshes, or requests user credentials."""
    user_dir = os.path.join(os.getcwd(), "users", user_email)
    os.makedirs(user_dir, exist_ok=True)
    token_path = os.path.join(user_dir, 'token.json')

    creds = None

    # ✅ Load existing token if available
    if os.path.exists(token_path):
        try:
            creds = Credentials.from_authorized_user_file(token_path, SCOPES)
            logging.info(f"✅ Loaded token for {user_email}")
        except Exception as e:
            logging.warning(f"⚠️ Failed to load token file: {e}")

    # 🔄 Refresh or obtain new credentials
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            try:
                creds.refresh(Request())
                logging.info("🔄 Token refreshed successfully.")
            except Exception:
                st.error("❌ Session expired. Please log in again.")
                creds = None

        if not creds:
            secret_path = _get_cached_secret_path()
            flow = InstalledAppFlow.from_client_secrets_file(secret_path, SCOPES)
            auth_url, _ = flow.authorization_url(prompt='consent', access_type='offline')
            st.markdown(f"[Click here to authenticate with Google]({auth_url})", unsafe_allow_html=True)
            return None

    return creds
