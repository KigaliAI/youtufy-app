# backend/auth.py

import os
import streamlit as st
import sqlite3
from dotenv import load_dotenv
from werkzeug.security import generate_password_hash, check_password_hash

# ✅ Load environment variables
load_dotenv()

# ✅ Get DB path from Streamlit secrets or fallback
DB_PATH = st.secrets.get("USER_DB", "data/YouTufy_users.db")


# 🔐 Hash Password
def hash_password(password: str) -> str:
    return generate_password_hash(password)


# 🔐 Check Password
def check_password(hashed_password: str, password: str) -> bool:
    return check_password_hash(hashed_password, password)


# ✅ Validate login
def validate_user(email: str, password: str) -> bool:
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("SELECT password FROM users WHERE email = ?", (email,))
        row = cursor.fetchone()
        conn.close()

        if row and check_password(row[0], password):
            return True
    except Exception as e:
        print(f"❌ Error validating user: {e}")

    return False


# 🔎 Get full user data (optional)
def get_user_by_email(email: str):
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("SELECT email, username, password FROM users WHERE email = ?", (email,))
        user = cursor.fetchone()
        conn.close()
        return user
    except Exception as e:
        print(f"❌ Error fetching user: {e}")
        return None


# ✅ Store credentials securely (for Google login)
def store_oauth_credentials(creds, user_email: str):
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("""
            INSERT OR REPLACE INTO users (email, google_creds)
            VALUES (?, ?)
        """, (user_email, creds.to_json()))
        conn.commit()
        conn.close()
    except Exception as e:
        print(f"❌ Failed to store OAuth credentials: {e}")
