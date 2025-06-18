# backend/auth.py

import sqlite3
import hashlib
import os
from dotenv import load_dotenv

# ✅ Load environment variables
load_dotenv()
DB_PATH = st.secrets["USER_DB"]

# 🔐 Password Hashing
def hash_password(password: str) -> str:
    """Securely hash passwords using SHA256."""
    return hashlib.sha256(password.encode()).hexdigest()

# 🔍 Authenticate User
def authenticate_user(email: str, password: str):
    """Validate user email and password against stored database records."""
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

# 🆕 Create New User
def create_user(email: str, username: str, password: str):
    """Create a new user with a hashed password (unverified by default)."""
    hashed = hash_password(password)
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("""
        INSERT INTO users (email, username, password, verified)
        VALUES (?, ?, ?, ?)
    """, (email, username, hashed, 0))
    conn.commit()
    conn.close()

# ✅ Verify User Email
def verify_user(email: str):
    """Set a user's verified flag to true."""
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("UPDATE users SET verified = 1 WHERE email = ?", (email,))
    conn.commit()
    conn.close()

# 🔁 Update Password
def update_password(email: str, new_password: str):
    """Update the user's password with a newly hashed one."""
    hashed = hash_password(new_password)
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("UPDATE users SET password = ? WHERE email = ?", (hashed, email))
    conn.commit()
    conn.close()

# 🔎 Check User Existence
def user_exists(email: str) -> bool:
    """Check whether a user already exists by email."""
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("SELECT 1 FROM users WHERE email=?", (email,))
    exists = cur.fetchone() is not None
    conn.close()
    return exists
