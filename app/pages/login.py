import os
import sys
import sqlite3
import hashlib
import streamlit as st
from dotenv import load_dotenv

# ✅ Adjust import path for utility modules
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', 'utils')))

# ✅ Streamlit page config
st.set_page_config(page_title="Login", layout="centered")
st.title("🔐 Login to YouTufy")

# ✅ Load environment variables
load_dotenv()
DB_PATH = os.getenv("USER_DB", "data/YouTufy_users.db")

# ✅ Hashing function for password
def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

# ✅ Authenticate user against DB
def authenticate_user(email, password):
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("SELECT username, password, verified FROM users WHERE email = ?", (email,))
    row = cur.fetchone()
    conn.close()
    if row:
        db_username, db_password, verified = row
        if hash_password(password) == db_password:
            return db_username, verified
    return None, False

# ✅ Login form
with st.form("login_form"):
    email = st.text_input("📧 Email", placeholder="you@example.com")
    password = st.text_input("🔒 Password", type="password")
    login_button = st.form_submit_button("Login")

# ✅ Login logic
if login_button:
    username, verified = authenticate_user(email, password)
    if username:
        if not verified:
            st.error("❌ Your account isn't verified yet.")
            st.info("📧 Please check your inbox for a verification link, or contact the admin to resend it.")
        else:
            st.session_state.user = email
            st.session_state.username = username
            st.success(f"✅ Welcome back, {username}!")
            st.switch_page("main.py")
    else:
        st.error("❌ Invalid email or password.")

# ✅ Extra: Forgot password
st.markdown("---")
if st.button("🔑 Forgot Password?"):
    st.switch_page("pages/reset_password.py")
