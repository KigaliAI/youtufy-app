# backend/auth.py

import os
import streamlit as st
import sqlite3
from dotenv import load_dotenv
from werkzeug.security import generate_password_hash, check_password_hash

load_dotenv()

DB_PATH = st.secrets.get("USER_DB", "data/YouTufy_users.db")

def hash_password(password: str) -> str:
    return generate_password_hash(password)

def check_password(hashed_password: str, password: str) -> bool:
    return check_password_hash(hashed_password, password)

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

def get_user_by_email(email: str):
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("SELECT email, password, verified, token, token_expiry FROM users WHERE email = ?", (email,))
        user = cursor.fetchone()
        conn.close()
        return user
    except Exception as e:
        print(f"❌ Error fetching user: {e}")
        return None

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

def get_email_from_token(token: str) -> str | None:
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("SELECT email FROM users WHERE token = ?", (token,))
    row = cur.fetchone()
    conn.close()
    return row[0] if row else None

