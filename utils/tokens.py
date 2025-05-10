import hashlib
import secrets
import time
import os
from dotenv import load_dotenv

load_dotenv()

# Load salt securely
SALT = os.getenv("TOKEN_SALT", "YouTufyDefaultSalt")


def generate_token(email: str) -> str:
    """
    Generate a secure token using SHA-256 hash of email, time, salt, and randomness.
    This token is used for email verification or password reset.
    """
    timestamp = str(time.time())
    random_hex = secrets.token_hex(16)
    raw_string = f"{email}|{timestamp}|{SALT}|{random_hex}"
    return hashlib.sha256(raw_string.encode()).hexdigest()


def validate_token(token: str) -> str | None:
    """
    Looks up the user associated with the given token in the database.
    You must have stored the token in your DB during registration/reset step.
    Returns the email if matched, else None.
    (This function should be implemented based on your DB structure.)
    """
    import sqlite3

    DB_PATH = os.getenv("USER_DB_PATH", "data/YouTufy_users.db")
    try:
        conn = sqlite3.connect(DB_PATH)
        cur = conn.cursor()
        cur.execute("SELECT email FROM users WHERE token = ?", (token,))
        row = cur.fetchone()
        conn.close()
        if row:
            return row[0]
    except Exception as e:
        print(f"❌ Token validation error: {e}")
    return None


def verify_token(provided_token: str, stored_token: str) -> bool:
    """
    Basic comparison between provided and stored tokens.
    Can be extended to check for expiration.
    """
    return provided_token == stored_token
