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
# 🔑 Function to retrieve cached secret path
# ----------------------------------
def _get_cached_secret_path():
    """Returns the cached OAuth secret file path."""
    secret_path = st.secrets.get("OAUTH_SECRET_PATH", None)

    if not secret_path or not os.path.exists(secret_path):
        logging.error("❌ Missing OAuth secret file. Please verify setup.")  # ✅ Use logging for production
        return None

    return secret_path

# ----------------------------------
# 🔑 Generate OAuth login URL
# ----------------------------------
def generate_auth_url_for_user(user_email=None):
    """Always return authentication URL to allow Google login."""
    secret_path = _get_cached_secret_path()
    if not secret_path:
        logging.error("❌ Authentication failed: OAuth secret file missing.")
        return None

    try:
        flow = InstalledAppFlow.from_client_secrets_file(secret_path, SCOPES)
        auth_url, _ = flow.authorization_url(prompt='consent', access_type='offline')
        return auth_url  # ✅ Redirects user to Google's authentication page
    except Exception as e:
        logging.error(f"❌ Error generating auth URL: {e}")
        return None

# ✅ Fix: `user_email` is now optional to prevent login errors

# ----------------------------------
# 🔑 Retrieve or refresh user credentials
# ----------------------------------
def get_user_credentials(user_email):
    """Loads, refreshes, or requests user credentials."""

    if not user_email:
        logging.warning("⚠️ No user email provided for credentials lookup.")
        return None

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
            except Exception as e:
                logging.error(f"❌ Token refresh failed: {e}")
                return None  # ✅ Stop execution if refresh fails

        if not creds:
            secret_path = _get_cached_secret_path()
            if not secret_path:
                logging.error("❌ Authentication failed: OAuth secret file missing.")
                return None

            try:
                flow = InstalledAppFlow.from_client_secrets_file(secret_path, SCOPES)
                auth_url, _ = flow.authorization_url(prompt='consent', access_type='offline')
                return None  # ✅ Prevent UI interruption for production
            except Exception as e:
                logging.error(f"❌ Error generating authentication flow: {e}")
                return None

    return creds
