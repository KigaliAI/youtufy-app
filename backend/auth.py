import os
import json
import logging
import streamlit as st
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request

# ----------------------------------
# 🔐 SCOPES & REDIRECT URI
# ----------------------------------
SCOPES = ['https://www.googleapis.com/auth/youtube.readonly']
REDIRECT_URI = st.secrets.get("OAUTH_REDIRECT_URI", "http://localhost:8501/")

# ----------------------------------
# 🔐 Store OAuth Credentials in Session (and optionally file/db)
# ----------------------------------
def store_oauth_credentials(creds, user_email):
    """Stores full OAuth credentials in session state and optionally disk."""
    if creds and creds.valid:
        creds_json = creds.to_json()
        st.session_state["google_creds"] = creds_json
        st.session_state["user"] = user_email
        st.session_state["authenticated"] = True
        logging.info(f"✅ Stored credentials in session for {user_email}")

        # Optional: persist to disk or DB
        path = f"users/{user_email.replace('@', '_at_')}_creds.json"
        os.makedirs("users", exist_ok=True)
        with open(path, "w") as f:
            f.write(creds_json)

# ----------------------------------
# 🔑 Retrieve and Refresh User Credentials
# ----------------------------------
def get_user_credentials(user_email):
    """Loads credentials from session or disk and refreshes if expired."""
    logging.debug("🔧 Debug: loading user credentials...")

    creds = None

    # 1. Try loading from session
    if "google_creds" in st.session_state:
        creds = Credentials.from_authorized_user_info(json.loads(st.session_state["google_creds"]), SCOPES)
    else:
        # 2. Try loading from disk
        path = f"users/{user_email.replace('@', '_at_')}_creds.json"
        if os.path.exists(path):
            with open(path, "r") as f:
                creds = Credentials.from_authorized_user_info(json.load(f), SCOPES)

    # 3. Refresh if needed
    if creds and creds.expired and creds.refresh_token:
        try:
            creds.refresh(Request())
            store_oauth_credentials(creds, user_email)
            logging.info("🔁 Refreshed expired token.")
        except Exception as e:
            logging.error(f"❌ Failed to refresh token: {e}")
            return None

    if creds and creds.valid:
        return creds

    logging.warning("⚠️ No valid credentials available.")
    return None
