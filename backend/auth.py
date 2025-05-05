import os
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from dotenv import load_dotenv

load_dotenv()

SCOPES = ['https://www.googleapis.com/auth/youtube.readonly']
REDIRECT_URI = "https://kigaliai.github.io/YouTufy/authorized.html"  # ✅ check in Web OAuth client, later add https://youtufy.app/auth/callback 

def get_user_credentials(user_email):
    user_dir = f"users/{user_email}"
    os.makedirs(user_dir, exist_ok=True)
    token_path = os.path.join(user_dir, 'token.json')
    creds = None

    if os.path.exists(token_path):
        creds = Credentials.from_authorized_user_file(token_path, SCOPES)

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            secret_path = os.getenv("GOOGLE_CLIENT_SECRET_PATH")
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

    return creds

def generate_auth_url_for_user(user_email):
    secret_path = os.getenv("GOOGLE_CLIENT_SECRET_PATH")
    flow = InstalledAppFlow.from_client_secrets_file(
        secret_path,
        SCOPES,
        redirect_uri=REDIRECT_URI  # ✅ Must match your Web app config
    )

    auth_url, _ = flow.authorization_url(prompt='consent', access_type='offline')
    return auth_url