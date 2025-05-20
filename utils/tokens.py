from itsdangerous import URLSafeTimedSerializer, BadSignature, SignatureExpired
import os
from dotenv import load_dotenv

load_dotenv()

SECRET_KEY = os.getenv("SECRET_KEY", "SuperSecretYouTufyKey")
TOKEN_SALT = os.getenv("TOKEN_SALT", "YouTufyTokenSalt")

# Create serializer
serializer = URLSafeTimedSerializer(secret_key=SECRET_KEY)


def generate_token(email: str) -> str:
    """
    Generate a signed, time-safe token based on the user's email.
    """
    return serializer.dumps(email, salt=TOKEN_SALT)


def verify_token(token: str, max_age_seconds=3600) -> str or None:
    """
    Verify the token is valid and not expired.
    Returns the original email if valid, or None.
    """
    try:
        email = serializer.loads(token, salt=TOKEN_SALT, max_age=max_age_seconds)
        return email
    except SignatureExpired:
        print("❌ Token expired.")
        return None
    except BadSignature:
        print("❌ Invalid token signature.")
        return None


# Optional: Validate against stored token (if needed)
def match_token(provided_token: str, stored_token: str) -> bool:
    return provided_token == stored_token
