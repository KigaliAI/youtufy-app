#utils/tokens.py
import hashlib
import secrets
import time
import os
from dotenv import load_dotenv

load_dotenv()

SALT = os.getenv("TOKEN_SALT", "YouTufyDefaultSalt")
EXPIRATION_SECONDS = int(os.getenv("TOKEN_EXPIRATION", 3600))  # Default: 1 hour


def generate_token(email: str) -> str:
    """
    Generate a token with embedded timestamp for validation.
    Format: <token>.<timestamp>
    """
    timestamp = str(int(time.time()))
    random_hex = secrets.token_hex(16)
    raw_string = f"{email}|{timestamp}|{SALT}|{random_hex}"
    token = hashlib.sha256(raw_string.encode()).hexdigest()
    return f"{token}.{timestamp}"


def verify_token(provided_token: str, stored_token: str) -> bool:
    """
    Validate the token hash and ensure it's not expired.
    """
    try:
        provided_hash, provided_ts = provided_token.split(".")
        stored_hash, stored_ts = stored_token.split(".")

        # Ensure token content matches
        if provided_hash != stored_hash:
            return False

        # Check expiration
        current_ts = int(time.time())
        token_ts = int(provided_ts)
        if (current_ts - token_ts) > EXPIRATION_SECONDS:
            return False

        return True
    except Exception as e:
        print("❌ Token verification error:", e)
        return False
