import streamlit as st
import sqlite3
from utils.tokens import validate_token

st.set_page_config(page_title="Verify Account", layout="centered")
st.title("🔐 Verify Your Email")

# Get token from query param
token = st.query_params.get("token")

if not token:
    st.warning("Missing verification token in the URL.")
    st.stop()

# Validate token
email = validate_token(token)

if not email:
    st.error("Invalid or expired token.")
    st.stop()

# Update DB to mark user as verified
db_path = "data/YouTufy_users.db"
conn = sqlite3.connect(db_path)
c = conn.cursor()
c.execute("UPDATE users SET verified = 1 WHERE email = ?", (email,))
conn.commit()
conn.close()

st.success(f"✅ Email verified for: {email}")
st.info("You can now return to the app and log in.")
st.page_link("/login", label="Go to Login", icon="➡️")