import hashlib
import secrets
import time
import os
from dotenv import load_dotenv

load_dotenv()

# Use the salt from .env or fallback
SALT = os.getenv("TOKEN_SALT", "YouTufyDefaultSalt")


def generate_token(email: str) -> str:
    """
    Generate a token based on email + salt.
    """
    raw = f"{email}|{SALT}"
    return hashlib.sha256(raw.encode()).hexdigest()


def validate_token(token: str) -> str or None:
    """
    Validate token by regenerating from all known emails in DB.
    Return matching email if valid.
    """
    import sqlite3
    DB_PATH = os.getenv("USER_DB_PATH", "data/YouTufy_users.db")

    try:
        conn = sqlite3.connect(DB_PATH)
        cur = conn.cursor()
        cur.execute("SELECT email FROM users")
        for (email,) in cur.fetchall():
            expected_token = generate_token(email)
            if expected_token == token:
                return email
        conn.close()
    except Exception as e:
        print(f"❌ Token validation DB error: {e}")

    return None


def verify_token(provided_token: str, stored_token: str) -> bool:
    """
    Compare raw token strings. Only used if storing tokens.
    """
    return provided_token == stored_token
