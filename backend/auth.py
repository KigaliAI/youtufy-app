import os
import tempfile
import streamlit as st
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request

# ----------------------------------
# 🔐 SCOPES & REDIRECT URI
# ----------------------------------
SCOPES = ['https://www.googleapis.com/auth/youtube.readonly']

# ✅ Update this to match your Streamlit app domain
REDIRECT_URI = "https://youtufy-one.streamlit.app/"

# ----------------------------------
# 🔎 Resolve OAuth client secret path
# ----------------------------------
def _get_secret_path():
    # ✅ Option A: Use JSON from Streamlit Secrets (production)
    if "GOOGLE_CLIENT_SECRET_JSON" in st.secrets:
        json_data = st.secrets["GOOGLE_CLIENT_SECRET_JSON"]

        # Write JSON string to a temporary file
        temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".json", mode="w")
        temp_file.write(json_data)
        temp_file.close()

        print(f"✅ Temp client_secret.json written to: {temp_file.name}")
        return temp_file.name

    # 🧪 Fallback: use local file for dev
    fallback_path = os.path.join("config", "client_secret.json")
    if os.path.exists(fallback_path):
        print(f"🧪 Using local client_secret.json at: {fallback_path}")
        return fallback_path

    # ❌ No file found
    raise FileNotFoundError("❌ No client secret JSON available from secrets or local path.")

# ----------------------------------
# 🔑 Retrieve user credentials
# ----------------------------------
def get_user_credentials(user_email):
    # Set up user-specific token directory
    user_dir = os.path.join(os.getcwd(), "users", user_email)
    os.makedirs(user_dir, exist_ok=True)
    token_path = os.path.join(user_dir, 'token.json')

    creds = None

    # Try loading saved token
    if os.path.exists(token_path):
        try:
            creds = Credentials.from_authorized_user_file(token_path, SCOPES)
            print(f"✅ Loaded existing token for {user_email}")
        except Exception as e:
            print(f"⚠️ Failed to load token: {e}")

    # If no valid creds, start OAuth flow
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            try:
                creds.refresh(Request())
                print("🔄 Token refreshed successfully.")
            except Exception as e:
                print(f"❌ Token refresh failed: {e}")
                creds = None
        else:
            # First-time auth flow
            secret_path = _get_secret_path()
            flow = InstalledAppFlow.from_client_secrets_file(
                secret_path,
                SCOPES,
                redirect_uri=REDIRECT_URI
            )
            auth_url, _ = flow.authorization_url(prompt='consent', access_type='offline')

            print(f"\n🔗 Visit this URL to authorize access:\n{auth_url}")
            code = input("🔑 Paste the code from Google here:\n").strip()

            flow.fetch_token(code=code)
            creds = flow.credentials

            # Save new token
            with open(token_path, 'w') as token_file:
                token_file.write(creds.to_json())
                print(f"✅ New token saved for {user_email} at {token_path}")

    return creds

# ----------------------------------
# 🌐 Generate login URL for frontend use
# ----------------------------------
def generate_auth_url_for_user(user_email):
    secret_path = _get_secret_path()
    flow = InstalledAppFlow.from_client_secrets_file(
        secret_path,
        SCOPES,
        redirect_uri=REDIRECT_URI
    )
    auth_url, _ = flow.authorization_url(prompt='consent', access_type='offline')
    return auth_url
