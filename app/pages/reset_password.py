import os
import sys
import streamlit as st
import sqlite3
import re
import hashlib

# Fix path for imports
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
sys.path.insert(0, project_root)

from utils.tokens import generate_token, validate_token

st.set_page_config(page_title="Reset Password", layout="centered")
st.title("🔑 Reset Your YouTufy Password")

DB_PATH = st.secrets.get("USER_DB_PATH", "data/YouTufy_users.db")

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

def update_password(email, password):
    try:
        conn = sqlite3.connect(DB_PATH)
        cur = conn.cursor()
        cur.execute("UPDATE users SET password = ?, token = NULL WHERE email = ?", (hash_password(password), email))
        conn.commit()
        conn.close()
        return True
    except Exception as e:
        st.error(f"❌ Failed to update password: {e}")
        return False

token = st.query_params.get("token")
if not token:
    st.warning("⚠️ No reset token provided.")
    st.stop()

email = validate_token(token)
if not email:
    st.error("❌ Invalid or expired token.")
    st.stop()

st.write(f"🔐 Resetting password for: **{email}**")
with st.form("reset_form"):
    new_pw = st.text_input("New Password", type="password")
    confirm_pw = st.text_input("Confirm Password", type="password")
    submitted = st.form_submit_button("Reset Password")

if submitted:
    if not new_pw or not confirm_pw:
        st.error("❗ Please fill in both password fields.")
    elif new_pw != confirm_pw:
        st.error("❗ Passwords do not match.")
    elif len(new_pw) < 6:
        st.error("❗ Password must be at least 6 characters long.")
    else:
        success = update_password(email, new_pw)
        if success:
            st.success("✅ Your password has been updated successfully!")
            st.page_link("/login", label="Go to Login", icon="➡️")

