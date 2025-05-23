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
        logging.error("❌ Missing OAuth secret file. Please verify setup.")
        return None

    return secret_path

# ----------------------------------
# 🔑 Generate OAuth login URL
# ----------------------------------
def generate_auth_url_for_user():
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

# ----------------------------------
# 🔐 Store OAuth Credentials in Session
# ----------------------------------
def store_oauth_credentials(creds):
    """Stores OAuth credentials in session state."""
    if creds and creds.valid:
        st.session_state["oauth_token"] = creds.token  # ✅ Store token
        st.session_state["user_authenticated"] = True  # ✅ Confirm login success
        logging.info("✅ Stored OAuth credentials in session.")

# ----------------------------------
# 🔑 Retrieve or refresh user credentials
# ----------------------------------
def get_user_credentials():
    """Loads, refreshes, or requests user credentials."""
    
    oauth_token = st.session_state.get("oauth_token")
    
    if not oauth_token:
        logging.warning("⚠️ No stored OAuth token found.")
        return None

    try:
        creds = Credentials(oauth_token)  # ✅ Use stored token
        if creds.expired and creds.refresh_token:
            creds.refresh(Request())  # ✅ Refresh expired token
            store_oauth_credentials(creds)  # ✅ Update stored credentials
            logging.info("🔄 Token refreshed successfully.")

        return creds

    except Exception as e:
        logging.error(f"❌ Error retrieving OAuth credentials: {e}")
        return None
