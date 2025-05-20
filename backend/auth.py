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
# 🗂️ Cache the temp secret path per session
# ----------------------------------
@st.cache_resource
def _get_cached_secret_path():
    """Retrieve Google client secret file and cache it."""
    if "GOOGLE_CLIENT_SECRET_JSON" in st.secrets:
        json_data = st.secrets["GOOGLE_CLIENT_SECRET_JSON"]
        temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".json", mode="w")
        temp_file.write(json_data)
        temp_file.close()
        logging.info(f"✅ Temp client_secret.json cached at: {temp_file.name}")
        return temp_file.name

    fallback_path = os.path.join("config", "client_secret.json")
    if os.path.exists(fallback_path):
        logging.info(f"🧪 Using local client_secret.json at: {fallback_path}")
        return fallback_path

    raise FileNotFoundError("❌ No client secret JSON available.")

# ----------------------------------
# 🔑 Generate OAuth login URL (Ensures user can sign in)
# ----------------------------------
def generate_auth_url_for_user(user_email=None):
    """Always return authentication URL to allow Google login."""
    secret_path = _get_cached_secret_path()
    flow = InstalledAppFlow.from_client_secrets_file(secret_path, SCOPES)
    auth_url, _ = flow.authorization_url(prompt='consent', access_type='offline')
    return auth_url  # ✅ Redirects user to Google's authentication page

# ----------------------------------
# 🔄 Retrieve or refresh user credentials
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
