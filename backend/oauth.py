#backend/oauth.py
import streamlit as st
import sys
import json
import pandas as pd
from datetime import datetime
from dotenv import load_dotenv
from pathlib import Path
from google_auth_oauthlib.flow import Flow
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

# Constants
SCOPES = ["https://www.googleapis.com/auth/youtube.readonly"]
CREDENTIALS_DIR = Path("users")
CLIENT_CONFIG = json.loads(st.secrets["GOOGLE_CLIENT_SECRET"])

def get_auth_flow(user_email: str) -> Flow:
    """
    Create a Google OAuth Flow instance for the given user.
    """
    flow = Flow.from_client_config(
        CLIENT_CONFIG,
        scopes=SCOPES,
        redirect_uri=f"https://youtufy-one.streamlit.app/pages/oauth_callback.py?email={user_email}"
    )
    return flow

def get_credentials_from_code(code: str, redirect_uri: str):
    """
    Exchange the authorization code for OAuth 2.0 credentials.
    """
    flow = Flow.from_client_config(
        CLIENT_CONFIG,
        scopes=SCOPES,
        redirect_uri=redirect_uri,
    )
    flow.fetch_token(code=code)
    return flow.credentials

def save_user_credentials(user_email: str, credentials: Credentials):
    """
    Save the user's credentials to a secure JSON file.
    """
    CREDENTIALS_DIR.mkdir(exist_ok=True)
    user_path = CREDENTIALS_DIR / f"{user_email}_creds.json"
    with open(user_path, "w") as f:
        f.write(credentials.to_json())

def get_user_credentials(user_email: str) -> Credentials | None:
    """
    Load saved credentials for a user. Refresh them if expired.
    """
    user_path = CREDENTIALS_DIR / f"{user_email}_creds.json"
    if not user_path.exists():
        return None

    try:
        creds = Credentials.from_authorized_user_file(str(user_path), SCOPES)
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
            save_user_credentials(user_email, creds)
        return creds
    except Exception as e:
        print(f"❌ Failed to load credentials for {user_email}: {e}")
        return None

def revoke_user_credentials(user_email: str):
    """
    Delete stored credentials for a user (if logout or revocation needed).
    """
    user_path = CREDENTIALS_DIR / f"{user_email}_creds.json"
    if user_path.exists():
        user_path.unlink()

