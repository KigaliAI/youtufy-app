#backend/auth.py
import os
import sqlite3
import hashlib
from dotenv import load_dotenv

# Load environment variables
load_dotenv()
DB_PATH = os.getenv("USER_DB", "data/YouTufy_users.db")

# ------------------------------------
# 🔐 Helper: Hash Password
# ------------------------------------
def hash_password(password: str) -> str:
    return hashlib.sha256(password.encode()).hexdigest()

# ------------------------------------
# ✅ Authenticate User (Email + Password)
# ------------------------------------
def authenticate_user(email: str, password: str):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    try:
        cursor.execute("SELECT username, password, verified FROM users WHERE email = ?", (email,))
        row = cursor.fetchone()
        if row:
            db_username, db_password, verified = row
            if hash_password(password) == db_password:
                return db_username, verified
    finally:
        conn.close()

    return None, False

# ------------------------------------
# 🧪 Check if Email Exists
# ------------------------------------
def email_exists(email: str) -> bool:
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT 1 FROM users WHERE email = ?", (email,))
    exists = cursor.fetchone() is not None
    conn.close()
    return exists

# ------------------------------------
# 📥 Register New User
# ------------------------------------
def register_user(email: str, username: str, password: str, token: str):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    hashed_pw = hash_password(password)
    try:
        cursor.execute("""
            INSERT INTO users (email, username, password, token, verified)
            VALUES (?, ?, ?, ?, 0)
        """, (email, username, hashed_pw, token))
        conn.commit()
        return True
    except sqlite3.IntegrityError:
        return False
    finally:
        conn.close()

# ------------------------------------
# ✅ Verify User with Token
# ------------------------------------
def verify_user_token(token: str) -> bool:
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute("SELECT email FROM users WHERE token = ?", (token,))
    row = cursor.fetchone()

    if row:
        cursor.execute("UPDATE users SET verified = 1 WHERE token = ?", (token,))
        conn.commit()
        conn.close()
        return True

    conn.close()
    return False

# ------------------------------------
# ♻️ Reset Password
# ------------------------------------
def reset_password(email: str, new_password: str):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    hashed_pw = hash_password(new_password)
    cursor.execute("UPDATE users SET password = ? WHERE email = ?", (hashed_pw, email))
    conn.commit()
    conn.close()

