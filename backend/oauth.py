# backend/oauth.py

import streamlit as st
import json
from pathlib import Path
from google_auth_oauthlib.flow import Flow
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials

# ✅ Constants
SCOPES = ["https://www.googleapis.com/auth/youtube.readonly"]
CREDENTIALS_DIR = Path("users")
CREDENTIALS_DIR.mkdir(parents=True, exist_ok=True)

# ✅ Load client configuration from Streamlit secrets
CLIENT_CONFIG = json.loads(st.secrets["GOOGLE_CLIENT_SECRET"])

def get_flow(redirect_uri: str) -> Flow:
    """
    Return an OAuth Flow using client config from Streamlit secrets.
    """
    return Flow.from_client_config(
        CLIENT_CONFIG,
        scopes=SCOPES,
        redirect_uri=redirect_uri
    )

def get_auth_flow(user_email: str) -> Flow:
    """
    Create OAuth Flow for a specific user with redirect URI for callback.
    """
    redirect_uri = f"https://youtufy-one.streamlit.app/main?email={user_email}"
    return get_flow(redirect_uri)

def get_credentials_from_code(code: str, redirect_uri: str) -> Credentials:
    """
    Exchange authorization code for user credentials.
    """
    flow = get_flow(redirect_uri)
    flow.fetch_token(code=code)
    return flow.credentials

def save_user_credentials(user_email: str, credentials: Credentials):
    """
    Save credentials securely to disk using email as identifier.
    """
    path = CREDENTIALS_DIR / f"{user_email}_creds.json"
    with open(path, "w") as f:
        f.write(credentials.to_json())

def get_user_credentials(user_email: str) -> Credentials | None:
    """
    Load saved credentials for a user; refresh if expired.
    """
    path = CREDENTIALS_DIR / f"{user_email}_creds.json"
    if not path.exists():
        return None

    try:
        creds = Credentials.from_authorized_user_file(str(path), SCOPES)
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
            save_user_credentials(user_email, creds)
        return creds
    except Exception as e:
        print(f"❌ Failed to load credentials for {user_email}: {e}")
        return None

def refresh_credentials(cred_json: str) -> Credentials:
    """
    Refresh credentials from session JSON (already authorized).
    """
    try:
        creds = Credentials.from_authorized_user_info(json.loads(cred_json), SCOPES)
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        return creds
    except Exception as e:
        print("❌ Error refreshing credentials:", e)
        return None

def revoke_user_credentials(user_email: str):
    """
    Delete a user's saved credentials (logout or revoke).
    """
    path = CREDENTIALS_DIR / f"{user_email}_creds.json"
    if path.exists():
        path.unlink()
