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
REDIRECT_URI = "https://youtufy-one.streamlit.app/"

# ----------------------------------
# 🗂️ Cache the temp secret path per session to avoid rewriting
# ----------------------------------
@st.cache_resource
def _get_cached_secret_path():
    if "GOOGLE_CLIENT_SECRET_JSON" in st.secrets:
        json_data = st.secrets["GOOGLE_CLIENT_SECRET_JSON"]
        temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".json", mode="w")
        temp_file.write(json_data)
        temp_file.close()
        print(f"✅ Temp client_secret.json cached at: {temp_file.name}")
        return temp_file.name

    # Dev fallback
    fallback_path = os.path.join("config", "client_secret.json")
    if os.path.exists(fallback_path):
        print(f"🧪 Using local client_secret.json at: {fallback_path}")
        return fallback_path

    raise FileNotFoundError("❌ No client secret JSON available from secrets or local path.")

# ----------------------------------
# 🔑 Retrieve or refresh user credentials
# ----------------------------------
def get_user_credentials(user_email):
    user_dir = os.path.join(os.getcwd(), "users", user_email)
    os.makedirs(user_dir, exist_ok=True)
    token_path = os.path.join(user_dir, 'token.json')

    creds = None

    # Attempt to load existing token
    if os.path.exists(token_path):
        try:
            creds = Credentials.from_authorized_user_file(token_path, SCOPES)
            print(f"✅ Loaded token for {user_email}")
        except Exception as e:
            print(f"⚠️ Failed to load token file: {e}")

    # If token is invalid or missing
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            try:
                creds.refresh(Request())
                print("🔄 Token refreshed successfully.")
            except Exception as e:
                print(f"❌ Token refresh failed: {e}")
                creds = None

        if not creds:
            # Begin OAuth flow
            secret_path = _get_cached_secret_path()
            flow = InstalledAppFlow.from_client_secrets_file(
                secret_path,
                SCOPES,
                redirect_uri=REDIRECT_URI
            )
            auth_url, _ = flow.authorization_url(prompt='consent', access_type='offline')
            print(f"\n🔗 Visit this URL to authorize:\n{auth_url}")
            code = input("🔑 Paste the code from Google here:\n").strip()

            flow.fetch_token(code=code)
            creds = flow.credentials

            with open(token_path, 'w') as token_file:
                token_file.write(creds.to_json())
                print(f"✅ New token saved for {user_email}")

    return creds

# ----------------------------------
# 🌐 Generate OAuth login URL (for browser-based flows)
# ----------------------------------
def generate_auth_url_for_user(user_email):
    secret_path = _get_cached_secret_path()
    flow = InstalledAppFlow.from_client_secrets_file(
        secret_path,
        SCOPES,
        redirect_uri=REDIRECT_URI
    )
    auth_url, _ = flow.authorization_url(prompt='consent', access_type='offline')
    return auth_url
