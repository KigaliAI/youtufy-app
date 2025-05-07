import os
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from dotenv import load_dotenv

load_dotenv()

SCOPES = ['https://www.googleapis.com/auth/youtube.readonly']
REDIRECT_URI = "https://kigaliai.github.io/YouTufy/authorized.html"

def get_user_credentials(user_email):
    # Create user-specific token directory
    user_dir = os.path.join(os.getcwd(), "users", user_email)
    os.makedirs(user_dir, exist_ok=True)
    token_path = os.path.join(user_dir, 'token.json')
    
    creds = None

    try:
        if os.path.exists(token_path):
            print(f"✅ Loading credentials from: {token_path}")
            creds = Credentials.from_authorized_user_file(token_path, SCOPES)
        else:
            print(f"⚠️ Token file not found for user: {user_email}")
    except Exception as e:
        print(f"❌ Failed to load credentials: {e}")

    # Handle invalid or missing credentials
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            try:
                creds.refresh(Request())
                print("🔄 Token refreshed successfully.")
            except Exception as e:
                print(f"❌ Token refresh failed: {e}")
                creds = None
        else:
            # New user or no refresh token available
            secret_path = os.getenv("GOOGLE_CLIENT_SECRET_PATH")
            if not secret_path or not os.path.exists(secret_path):
                raise FileNotFoundError("❌ GOOGLE_CLIENT_SECRET_PATH is not set or file does not exist.")

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
                print(f"✅ Saved new token to: {token_path}")

    return creds

def generate_auth_url_for_user(user_email):
    secret_path = os.getenv("GOOGLE_CLIENT_SECRET_PATH")
    if not secret_path or not os.path.exists(secret_path):
        raise FileNotFoundError("❌ GOOGLE_CLIENT_SECRET_PATH is not set or file does not exist.")

    flow = InstalledAppFlow.from_client_secrets_file(
        secret_path,
        SCOPES,
        redirect_uri=REDIRECT_URI
    )

    auth_url, _ = flow.authorization_url(prompt='consent', access_type='offline')
    return auth_url
