import os
import json
import logging
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from dotenv import load_dotenv

load_dotenv()

SCOPES = ['https://www.googleapis.com/auth/youtube.readonly']
USER_DATA_DIR = "users"

# 🔐 Store OAuth credentials in a file
def store_oauth_credentials(creds, user_email):
    """Saves OAuth credentials for a user in a JSON token file."""
    if not user_email:
        logging.error("❌ store_oauth_credentials: user_email is missing.")
        return

    user_dir = os.path.join(USER_DATA_DIR, user_email)
    os.makedirs(user_dir, exist_ok=True)
    token_path = os.path.join(user_dir, "token.json")

    with open(token_path, "w") as f:
        f.write(creds.to_json())
    logging.info(f"✅ Stored credentials for {user_email}")

# 🔑 Load user credentials from file
def get_user_credentials(user_email):
    """Loads stored credentials or returns None if missing/invalid."""
    if not user_email:
        raise ValueError("❌ get_user_credentials: user_email must not be None")

    token_path = os.path.join(USER_DATA_DIR, user_email, "token.json")

    if not os.path.exists(token_path):
        logging.warning(f"⚠️ Token not found for {user_email}")
        return None

    try:
        creds = Credentials.from_authorized_user_file(token_path, SCOPES)

        if not creds.valid:
            if creds.expired and creds.refresh_token:
                creds.refresh(Request())
                store_oauth_credentials(creds, user_email)
                logging.info(f"🔄 Refreshed token for {user_email}")
            else:
                logging.warning(f"❌ Invalid or expired token for {user_email}")
                return None

        return creds

    except Exception as e:
        logging.error(f"❌ Failed to load credentials for {user_email}: {e}")
        return None
