# backend/oauth.py

import streamlit as st
import json
from pathlib import Path
from google_auth_oauthlib.flow import Flow
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials

# Constants
SCOPES = ["https://www.googleapis.com/auth/youtube.readonly"]
CREDENTIALS_DIR = Path("users")

# Load client configuration from secrets
CLIENT_CONFIG = json.loads(st.secrets["GOOGLE_CLIENT_SECRET"])

def get_flow(redirect_uri: str) -> Flow:
    """
    Create a new Google OAuth flow instance.
    """
    return Flow.from_client_config(
        CLIENT_CONFIG,
        scopes=SCOPES,
        redirect_uri=redirect_uri
    )

def get_auth_flow(user_email: str) -> Flow:
    """
    Create an OAuth flow specific to a user (with embedded redirect).
    """
    return get_flow(f"https://youtufy-one.streamlit.app/pages/oauth_callback.py?email={user_email}")

def get_credentials_from_code(code: str, redirect_uri: str) -> Credentials:
    """
    Exchange the authorization code for user credentials.
    """
    flow = get_flow(redirect_uri)
    flow.fetch_token(code=code)
    return flow.credentials

def save_user_credentials(user_email: str, credentials: Credentials):
    """
    Persist credentials securely to disk.
    """
    CREDENTIALS_DIR.mkdir(exist_ok=True)
    cred_path = CREDENTIALS_DIR / f"{user_email}_creds.json"
    with open(cred_path, "w") as f:
        f.write(credentials.to_json())

def get_user_credentials(user_email: str) -> Credentials | None:
    """
    Retrieve and optionally refresh saved credentials.
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
        print(f"❌ Error loading credentials for {user_email}: {e}")
        return None

def refresh_credentials(cred_json: str) -> Credentials:
    """
    Refresh credentials from a JSON string stored in session.
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
    Remove stored user credentials (e.g., on logout).
    """
    cred_path = CREDENTIALS_DIR / f"{user_email}_creds.json"
    if cred_path.exists():
        cred_path.unlink()
