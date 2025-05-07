import os
import streamlit as st
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request

SCOPES = ['https://www.googleapis.com/auth/youtube.readonly']
REDIRECT_URI = "https://kigaliai.github.io/YouTufy/authorized.html"

def _get_secret_path():
    # Use Streamlit secrets if running in production
    secret_path = st.secrets.get("GOOGLE_CLIENT_SECRET_PATH", None)

    # Fallback to local config if not found in secrets (e.g. dev mode)
    if not secret_path:
        local_path = os.path.join("config", "client_secret.json")
        print(f"🔍 Using fallback local secret path: {local_path}")
        secret_path = local_path

    # Check existence
    if not os.path.exists(secret_path):
        raise FileNotFoundError(f"❌ OAuth client secret file not found at: {secret_path}")

    print(f"🔐 Using client secret file from: {secret_path}")
    return secret_path

def get_user_credentials(user_email):
    # Token storage per user
    user_dir = os.path.join(os.getcwd(), "users", user_email)
    os.makedirs(user_dir, exist_ok=True)
    token_path = os.path.join(user_dir, 'token.json')

    creds = None

    # Try to load existing credentials
    if os.path.exists(token_path):
        print(f"✅ Loading token for {user_email}")
        creds = Credentials.from_authorized_user_file(token_path, SCOPES)
    else:
        print(f"⚠️ No token found for {user_email}")

    # Refresh or request new token
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            try:
                creds.refresh(Request())
                print("🔄 Token refreshed.")
            except Exception as e:
                print(f"❌ Token refresh error: {e}")
                creds = None
        else:
            # First-time authorization
            secret_path = _get_secret_path()
            flow = InstalledAppFlow.from_client_secrets_file(
                secret_path,
                SCOPES,
                redirect_uri=REDIRECT_URI
            )
            auth_url, _ = flow.authorization_url(prompt='consent', access_type='offline')

            print(f"\n🔗 Please visit this URL to authorize:\n{auth_url}")
            code = input("🔑 Paste the code from Google here:\n").strip()

            flow.fetch_token(code=code)
            creds = flow.credentials

            with open(token_path, 'w') as token_file:
                token_file.write(creds.to_json())
                print(f"✅ Token saved at {token_path}")

    return creds

def generate_auth_url_for_user(user_email):
    secret_path = _get_secret_path()
    flow = InstalledAppFlow.from_client_secrets_file(
        secret_path,
        SCOPES,
        redirect_uri=REDIRECT_URI
    )
    auth_url, _ = flow.authorization_url(prompt='consent', access_type='offline')
    return auth_url
