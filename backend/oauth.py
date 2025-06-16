#backend/oauth.py
import os
import json
import requests
import streamlit as st
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import Flow
from google.auth.transport.requests import Request
from google.auth.exceptions import DefaultCredentialsError

# Constants
SCOPES = ["https://www.googleapis.com/auth/youtube.readonly"]
REDIRECT_URI = st.secrets.get(
    "OAUTH_REDIRECT_URI",
    "https://youtufy-one.streamlit.app/app/pages/google_login"
)
# ✅ OAuth Configuration
SCOPES = ["https://www.googleapis.com/auth/youtube.readonly"]
REDIRECT_URI = st.secrets.get("OAUTH_REDIRECT_URI", "https://youtufy-one.streamlit.app/main")

# ✅ Secure Credentials Storage
USER_DATA_DIR = "users"
os.makedirs(USER_DATA_DIR, exist_ok=True)

# 🔄 Check if Running on Google Cloud Compute Engine
def is_running_on_gce():
    """Prevent unnecessary metadata requests outside Google Cloud."""
    try:
        response = requests.get(
            "http://169.254.169.254/computeMetadata/v1/instance/",
            headers={"Metadata-Flavor": "Google"},
            timeout=2
        )
        return response.status_code == 200
    except requests.exceptions.RequestException:
        return False  # ✅ Not running inside GCE

# 🔑 Load OAuth Flow Configuration
def get_flow(redirect_uri=REDIRECT_URI):
    """Creates OAuth flow while preventing metadata lookup failures."""
    secret_path = st.secrets.get("GOOGLE_CLIENT_SECRET_PATH")
    json_string = st.secrets.get("GOOGLE_CLIENT_SECRET_JSON")

    if secret_path and os.path.exists(secret_path):
        return Flow.from_client_secrets_file(secret_path, SCOPES, redirect_uri=redirect_uri)
    elif json_string:
        try:
            client_config = json.loads(json_string)
            return Flow.from_client_config(client_config, SCOPES, redirect_uri=redirect_uri)
        except Exception as e:
            st.error("❌ Failed to parse embedded JSON.")
            raise e
    raise ValueError("❌ No valid Google client secret found.")

def get_credentials_from_code(code, redirect_uri=REDIRECT_URI):
    """Exchange authorization code for credentials and prevent reliance on GCE metadata."""
# 🔑 Exchange Authorization Code for Credentials
def get_credentials_from_code(code, redirect_uri=REDIRECT_URI):
    """Handles OAuth token exchange while preventing GCE metadata calls."""
    flow = get_flow(redirect_uri)
    flow.fetch_token(code=code)
    creds = flow.credentials
    if not creds or creds.invalid:
        raise RuntimeError("⚠️ OAuth authentication failed. Ensure credentials are properly configured.")
    
    return creds

    if not creds or creds.invalid:
        raise RuntimeError("⚠️ OAuth authentication failed.")

    # ✅ Explicitly disable GCE metadata lookup in credentials
    creds._quota_project_id = None  
    creds._enable_reauth_refresh = False  

    user_email = creds.id_token.get("email", None)
    if user_email:
        st.session_state["user"] = user_email
        st.session_state["username"] = user_email.split("@")[0]
        st.session_state["google_creds"] = creds.to_json()
        st.session_state["authenticated"] = True
        store_oauth_credentials(creds, user_email)

    return creds

# 💾 Store OAuth Credentials Securely
def store_oauth_credentials(creds, user_email):
    """Saves OAuth credentials for future authentication."""
    user_dir = os.path.join(USER_DATA_DIR, user_email)
    os.makedirs(user_dir, exist_ok=True)
    token_path = os.path.join(user_dir, "token.json")
    try:
        with open(token_path, "w") as f:
            f.write(creds.to_json())
        print(f"✅ Credentials saved at: {token_path}")
    except Exception as e:
        print(f"❌ Failed to save credentials: {e}")

# 🔄 Load and Refresh OAuth Credentials
def get_user_credentials(user_email):
    """Loads stored OAuth credentials while blocking metadata API errors."""
    token_path = os.path.join(USER_DATA_DIR, user_email, "token.json")

    if not os.path.exists(token_path):
        print("⚠️ No token file found.")
        return None

    try:
        creds = Credentials.from_authorized_user_file(token_path, SCOPES)

        # ✅ Explicitly prevent GCE metadata server requests before refreshing
        creds._quota_project_id = None
        creds._enable_reauth_refresh = False

        if creds.expired and creds.refresh_token:
            creds.refresh(Request())
            store_oauth_credentials(creds, user_email)
            try:
                creds.refresh(Request())
                store_oauth_credentials(creds, user_email)
            except Exception as e:
                print(f"⚠️ Failed to refresh credentials: {e}")
                return None
        return creds
    except Exception as e:
        print(f"❌ Failed to load/refresh credentials: {e}")
        return None
