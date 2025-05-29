# backend/oauth.py

import os
from google_auth_oauthlib.flow import Flow
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

SCOPES = ['https://www.googleapis.com/auth/youtube.readonly']
CLIENT_SECRET_PATH = os.getenv("GOOGLE_CLIENT_SECRET_PATH")
REDIRECT_URI_DEFAULT = "https://youtufy-one.streamlit.app/dashboard"


def get_flow(redirect_uri=REDIRECT_URI_DEFAULT):
    """Initializes the OAuth Flow with client secrets and scopes."""
    return Flow.from_client_secrets_file(
        CLIENT_SECRET_PATH,
        scopes=SCOPES,
        redirect_uri=redirect_uri
    )


def get_credentials_from_code(code, redirect_uri=REDIRECT_URI_DEFAULT):
    """Exchanges an authorization code for credentials."""
    flow = get_flow(redirect_uri)
    flow.fetch_token(code=code)
    return flow.credentials


def refresh_credentials(creds_json):
    """Refreshes expired credentials using the refresh token."""
    creds = Credentials.from_authorized_user_info(eval(creds_json), SCOPES)
    if creds.expired and creds.refresh_token:
        creds.refresh(Request())
    return creds
