import hashlib
import secrets
import time
import os
from dotenv import load_dotenv

load_dotenv()

# Use the salt from .env or fallback to a default
SALT = os.getenv("TOKEN_SALT", "YouTufyDefaultSalt")

def generate_token(email: str) -> str:
    """
    Generate a secure verification token based on email, timestamp, and salt.
    """
    timestamp = str(time.time())
    random_hex = secrets.token_hex(16)
    raw_string = f"{email}|{timestamp}|{SALT}|{random_hex}"
    return hashlib.sha256(raw_string.encode()).hexdigest()

def verify_token(provided_token: str, stored_token: str) -> bool:
    """
    Compares a provided token with what's stored in the DB.
    Can be enhanced to include expiration.
    """
    return provided_token == stored_token
