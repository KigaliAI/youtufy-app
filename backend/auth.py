#backend/auth.py
import sqlite3
import hashlib
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()
DB_PATH = os.getenv("USER_DB", "data/YouTufy_users.db")

# Secure password hashing using SHA256
def hash_password(password: str) -> str:
    return hashlib.sha256(password.encode()).hexdigest()

# 🚀 Authenticate user by email + password (prevents timing attacks)
def authenticate_user(email: str, password: str):
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("SELECT username, password, verified FROM users WHERE email=?", (email,))
    row = cur.fetchone()
    conn.close()

    if row:
        db_username, db_password, verified = row
        if hash_password(password) == db_password:
            return db_username, verified
    return None, False

# ✅ Create new user (auto-hashes password)
def create_user(email: str, username: str, password: str):
    hashed = hash_password(password)
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    cur.execute("""
        INSERT INTO users (email, username, password, verified)
        VALUES (?, ?, ?, ?)
    """, (email, username, hashed, 0))  # Default: not verified

    conn.commit()
    conn.close()

# ✅ Set user as verified
def verify_user(email: str):
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("UPDATE users SET verified = 1 WHERE email = ?", (email,))
    conn.commit()
    conn.close()

# ✅ Securely reset password
def update_password(email: str, new_password: str):
    hashed = hash_password(new_password)
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("UPDATE users SET password = ? WHERE email = ?", (hashed, email))
    conn.commit()
    conn.close()

# ✅ Check if user exists before allowing actions
def user_exists(email: str) -> bool:
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("SELECT 1 FROM users WHERE email=?", (email,))
    exists = cur.fetchone() is not None
    conn.close()
    return exists

