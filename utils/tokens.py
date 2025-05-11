import hashlib
import secrets
import time
import os
import sqlite3
from dotenv import load_dotenv

load_dotenv()
SALT = os.getenv("TOKEN_SALT", "YouTufyDefaultSalt")
DB_PATH = os.getenv("USER_DB_PATH", "data/YouTufy_users.db")

def generate_token(email: str) -> str:
    timestamp = str(time.time())
    random_hex = secrets.token_hex(16)
    raw_string = f"{email}|{timestamp}|{SALT}|{random_hex}"
    token = hashlib.sha256(raw_string.encode()).hexdigest()

    try:
        conn = sqlite3.connect(DB_PATH)
        cur = conn.cursor()
        cur.execute("UPDATE users SET token = ? WHERE email = ?", (token, email))
        conn.commit()
        conn.close()
    except Exception as e:
        print(f"❌ Failed to store token in DB: {e}")

    return token

def validate_token(token: str) -> str:
    try:
        conn = sqlite3.connect(DB_PATH)
        cur = conn.cursor()
        cur.execute("SELECT email FROM users WHERE token = ?", (token,))
        result = cur.fetchone()
        conn.close()
        return result[0] if result else None
    except Exception as e:
        print(f"❌ Token validation error: {e}")
        return None
