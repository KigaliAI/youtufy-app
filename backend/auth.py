# backend/auth.py

import hashlib
import streamlit as st
import sqlite3
import os
from dotenv import load_dotenv

# ✅ Load environment
load_dotenv()
DB_PATH = st.secrets.get("USER_DB", "data/YouTufy_users.db")

# 🔐 Password Hashing
def hash_password(password: str) -> str:
    """
    Returns a SHA-256 hash of the given password.
    """
    return hashlib.sha256(password.encode()).hexdigest()

def check_password(password: str, hashed: str) -> bool:
    """
    Compares a plaintext password with its hashed version.
    """
    return hash_password(password) == hashed

# 🔐 SQLite: Save OAuth credentials
def store_oauth_credentials(creds, email):
    """
    Optionally store OAuth credentials in the database.
    (This function is defined for future extensions.)
    """
    pass  # You can expand this if you need persistent DB storage of credentials
