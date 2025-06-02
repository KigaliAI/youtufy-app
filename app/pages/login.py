import streamlit as st
import sqlite3
import hashlib
import hmac
import os
from dotenv import load_dotenv
from utils.tokens import generate_token  # Ensure this exists

# Page Configuration
st.set_page_config(page_title="Login", layout="centered")
st.title("🔐 Login to YouTufy")

# Load Environment Variables
load_dotenv()
DB_PATH = os.getenv("USER_DB", "data/YouTufy_users.db")

# Secure Password Hashing & Verification
def hash_password(password):
    """Hashes password securely."""
    return hashlib.sha256(password.encode()).hexdigest()

def verify_password(input_password, stored_password):
    """Prevents timing attacks using hmac.compare_digest."""
    return hmac.compare_digest(hash_password(input_password), stored_password)

# Authenticate User Function
def authenticate_user(email, password):
    """Checks the database for user credentials."""
    with sqlite3.connect(DB_PATH) as conn:
        cur = conn.cursor()
        cur.execute("SELECT username, password, verified FROM users WHERE email=?", (email,))
        row = cur.fetchone()

    if row:
        db_username, db_password, verified = row
        if verify_password(password, db_password):
            return db_username, verified
    return None, False

# Login Form
with st.form("login_form"):
    email = st.text_input("📧 Email")
    password = st.text_input("🔑 Password", type="password")
    login_button = st.form_submit_button("Login")

if login_button:
    username, verified = authenticate_user(email, password)
    if username:
        if not verified:
            st.error("❌ Your account is not yet verified. Please check your email.")
        else:
            st.session_state["user"] = email
            st.session_state["username"] = username
            st.success(f"✅ Welcome back, {username}!")

            # Ensure session state variables exist before switching pages
            if "user" in st.session_state and "username" in st.session_state:
                st.switch_page("main")  # No ".py"
            else:
                st.error("⚠️ Session data missing, please log in again.")

    else:
        st.error("❌ Invalid email or password.")

# Forgotten Password
st.markdown("---")
if st.button("🔑 Forgot Password?"):
    st.switch_page("reset_password")

# Google Login
st.markdown("### Or login with Google")
if st.button("🔐 Continue with Google"):
    st.switch_page("google_login")
