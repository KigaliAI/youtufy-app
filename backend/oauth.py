#backend/oauth.py
import streamlit as st
import json
from pathlib import Path
from google_auth_oauthlib.flow import Flow
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials

# Constants
SCOPES = ["https://www.googleapis.com/auth/youtube.readonly"]
CREDENTIALS_DIR = Path("users")

# Load Google OAuth client config from secrets.toml (Streamlit Cloud UI)
CLIENT_CONFIG = json.loads(st.secrets["GOOGLE_CLIENT_SECRET"])

def get_flow(redirect_uri: str) -> Flow:
    """
    Create a Google OAuth flow using Streamlit secrets and specified redirect URI.
    """
    return Flow.from_client_config(
        CLIENT_CONFIG,
        scopes=SCOPES,
        redirect_uri=redirect_uri
    )

def get_auth_flow(user_email: str) -> Flow:
    """
    Return Flow configured with redirect URI for OAuth callback.
    """
    redirect_uri = f"https://youtufy-one.streamlit.app/pages/oauth_callback.py?email={user_email}"
    return get_flow(redirect_uri)

def get_credentials_from_code(code: str, redirect_uri: str) -> Credentials:
    """
    Exchange the authorization code for credentials.
    """
    flow = get_flow(redirect_uri)
    flow.fetch_token(code=code)
    return flow.credentials

def save_user_credentials(user_email: str, credentials: Credentials):
    """
    Save credentials to a JSON file associated with the user.
    """
    CREDENTIALS_DIR.mkdir(parents=True, exist_ok=True)
    cred_path = CREDENTIALS_DIR / f"{user_email}_creds.json"
    with open(cred_path, "w") as f:
        f.write(credentials.to_json())

def get_user_credentials(user_email: str) -> Credentials | None:
    """
    Load user credentials and refresh them if expired.
    """
    cred_path = CREDENTIALS_DIR / f"{user_email}_creds.json"
    if not cred_path.exists():
        return None

    try:
        creds = Credentials.from_authorized_user_file(str(cred_path), SCOPES)
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
            save_user_credentials(user_email, creds)
        return creds
    except Exception as e:
        print(f"❌ Failed to load credentials for {user_email}: {e}")
        return None

def refresh_credentials(cred_json: str) -> Credentials:
    """
    Refresh credentials from session-stored JSON.
    """
    try:
        creds = Credentials.from_authorized_user_info(json.loads(cred_json), SCOPES)
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        return creds
    except Exception as e:
        print("❌ Failed to refresh credentials:", e)
        return None

def revoke_user_credentials(user_email: str):
    """
    Delete a user's saved credentials.
    """
    cred_path = CREDENTIALS_DIR / f"{user_email}_creds.json"
    if cred_path.exists():
        cred_path.unlink()

