import os
import json
import requests
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import Flow
from google.auth.transport.requests import Request
import streamlit as st

# Constants
SCOPES = ["https://www.googleapis.com/auth/youtube.readonly"]
REDIRECT_URI = st.secrets.get(
    "OAUTH_REDIRECT_URI",
    "https://youtufy-one.streamlit.app/app/pages/google_login"
)

USER_DATA_DIR = "users"
os.makedirs(USER_DATA_DIR, exist_ok=True)

def is_running_on_gce():
    """Check if running inside Google Cloud Compute Engine to prevent metadata issues."""
    try:
        response = requests.get(
            "http://169.254.169.254/computeMetadata/v1/instance/",
            headers={"Metadata-Flavor": "Google"},
            timeout=2
        )
        return response.status_code == 200
    except requests.exceptions.RequestException:
        return False  # Not running on GCE

def get_flow(redirect_uri=REDIRECT_URI):
    """Creates OAuth flow while ensuring authentication doesn't rely on GCE metadata."""
    if is_running_on_gce():
        raise RuntimeError("⚠️ Metadata access attempted outside GCE. Switching to manual authentication.")

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
    flow = get_flow(redirect_uri)
    flow.fetch_token(code=code)

    creds = flow.credentials
    if not creds or creds.invalid:
        raise RuntimeError("⚠️ OAuth authentication failed. Ensure credentials are properly configured.")
    
    return creds

def store_oauth_credentials(creds, user_email):
    """Securely save OAuth credentials."""
    user_dir = os.path.join(USER_DATA_DIR, user_email)
    os.makedirs(user_dir, exist_ok=True)
    token_path = os.path.join(user_dir, "token.json")
    try:
        with open(token_path, "w") as f:
            f.write(creds.to_json())
        print(f"✅ Credentials saved at: {token_path}")
    except Exception as e:
        print(f"❌ Failed to save credentials: {e}")

def get_user_credentials(user_email):
    """Load stored OAuth credentials, refresh if expired."""
    token_path = os.path.join(USER_DATA_DIR, user_email, "token.json")
    if not os.path.exists(token_path):
        print("⚠️ No token file found.")
        return None

    try:
        creds = Credentials.from_authorized_user_file(token_path, SCOPES)
        if creds.expired and creds.refresh_token:
            creds.refresh(Request())
            store_oauth_credentials(creds, user_email)
        return creds
    except Exception as e:
        print(f"❌ Failed to load/refresh credentials: {e}")
        return None
