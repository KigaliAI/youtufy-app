#backend/oauth.py
import os
import json
import streamlit as st
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import Flow
from google.auth.transport.requests import Request

# ------------------------------------
# 🔐 Google OAuth Configuration
# ------------------------------------
SCOPES = ["https://www.googleapis.com/auth/youtube.readonly"]

# Make sure this matches exactly the redirect URI set in Google Cloud Console
REDIRECT_URI = st.secrets.get(
    "OAUTH_REDIRECT_URI",
    "https://youtufy-one.streamlit.app/app/pages/google_login"
)

USER_DATA_DIR = "users"
os.makedirs(USER_DATA_DIR, exist_ok=True)

# ------------------------------------
# 📥 Load OAuth Flow
# ------------------------------------
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
            st.error("❌ Failed to parse embedded client secret JSON.")
            raise e

    raise ValueError("❌ No valid Google client secret found.")


# ------------------------------------
# 🔄 Exchange Code for Credentials
# ------------------------------------
def get_credentials_from_code(code, redirect_uri=REDIRECT_URI):
    flow = get_flow(redirect_uri)
    flow.fetch_token(code=code)
    return flow.credentials


# ------------------------------------
# ♻️ Refresh Credentials if Expired
# ------------------------------------
def refresh_credentials(json_creds):
    creds = Credentials.from_authorized_user_info(json.loads(json_creds), SCOPES)
    if creds and creds.expired and creds.refresh_token:
        creds.refresh(Request())
    return creds


# ------------------------------------
# 💾 Store Credentials to File
# ------------------------------------
def store_oauth_credentials(creds, user_email):
    try:
        user_dir = os.path.join(USER_DATA_DIR, user_email)
        os.makedirs(user_dir, exist_ok=True)
        token_path = os.path.join(user_dir, "token.json")
        with open(token_path, "w") as f:
            f.write(creds.to_json())
        print(f"✅ Credentials saved at: {token_path}")
    except Exception as e:
        print(f"⚠️ Could not save credentials for {user_email}: {e}")


# ------------------------------------
# 📂 Retrieve Stored Credentials
# ------------------------------------
def get_user_credentials(user_email):
    token_path = os.path.join(USER_DATA_DIR, user_email, "token.json")

    if not os.path.exists(token_path):
        print(f"⚠️ No token file found for user: {user_email}")
        return None

    try:
        creds = Credentials.from_authorized_user_file(token_path, SCOPES)
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
            store_oauth_credentials(creds, user_email)
        return creds
    except Exception as e:
        print(f"❌ Failed to load or refresh credentials: {e}")
        return None

