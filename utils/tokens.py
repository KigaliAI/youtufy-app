#utils/tokens.py
import sys
import hashlib
import secrets
import time
import os
from dotenv import load_dotenv
import streamlit as st

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))
load_dotenv()

SALT = st.secrets.get("TOKEN_SALT", "YouTufyDefaultSalt")
EXPIRATION_SECONDS = int(st.secrets.get("TOKEN_EXPIRATION", 3600))  # Default: 1 hour

def generate_token(email: str) -> str:
    timestamp = str(int(time.time()))
    random_hex = secrets.token_hex(16)
    raw_string = f"{email}|{timestamp}|{SALT}|{random_hex}"
    token = hashlib.sha256(raw_string.encode()).hexdigest()
    return f"{token}.{timestamp}"

def verify_token(provided_token: str, stored_token: str) -> bool:
    try:
        provided_hash, provided_ts = provided_token.split(".")
        stored_hash, stored_ts = stored_token.split(".")

        if provided_hash != stored_hash:
            return False

        current_ts = int(time.time())
        token_ts = int(provided_ts)
        return (current_ts - token_ts) <= EXPIRATION_SECONDS
    except Exception as e:
        print("Token verification failed:", e)
        return False

def decode_token(token: str) -> str | None:
    # Stub: override with logic that returns email for a given token
    return None

