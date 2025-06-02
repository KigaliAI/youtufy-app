# Updated: backend/oauth.py
import os
import json
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

# Load OAuth flow using either file path or embedded JSON
def get_flow(redirect_uri=REDIRECT_URI):
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

# Exchange code for credentials
def get_credentials_from_code(code, redirect_uri=REDIRECT_URI):
    flow = get_flow(redirect_uri)
    flow.fetch_token(code=code)
    return flow.credentials

# Refresh credentials if expired
def refresh_credentials(json_creds):
    creds = Credentials.from_authorized_user_info(json.loads(json_creds), SCOPES)
    if creds and creds.expired and creds.refresh_token:
        creds.refresh(Request())
    return creds
