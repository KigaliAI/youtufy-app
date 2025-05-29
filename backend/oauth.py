# backend/oauth.py
import json
import streamlit as st
from google_auth_oauthlib.flow import Flow
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request

# Define required scope
SCOPES = ['https://www.googleapis.com/auth/youtube.readonly']


def get_flow(redirect_uri):
    """
    Create and return a Google OAuth flow using secrets from Streamlit.
    Loads the client config from embedded JSON in secrets.toml.
    """
    secret_json = st.secrets["GOOGLE_CLIENT_SECRET_JSON"]
    client_config = json.loads(secret_json)
    return Flow.from_client_config(client_config, SCOPES, redirect_uri=redirect_uri)


def get_credentials_from_code(code, redirect_uri):
    """
    Exchange an authorization code for OAuth credentials.
    """
    flow = get_flow(redirect_uri)
    flow.fetch_token(code=code)
    return flow.credentials


def refresh_credentials(creds_json):
    """
    Refresh stored credentials if expired.
    """
    creds = Credentials.from_authorized_user_info(json.loads(creds_json), SCOPES)

    if creds and creds.expired and creds.refresh_token:
        creds.refresh(Request())

    return creds
