#app/pages/update_password.py
import sys
import os
import inspect
import utils.tokens

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

import streamlit as st
from utils.tokens import verify_token, decode_token
from backend.auth import update_user_password, get_email_from_token
import time

st.set_page_config(page_title="Reset Password", layout="centered")
st.title("🔑 Reset Your Password")

token = st.query_params.get("token")
if not token:
    st.error("Missing token in URL.")
    st.stop()

print("✅ Available functions in tokens.py:", dir(utils.tokens))
print("📄 decode_token source:", inspect.getsource(utils.tokens.decode_token))

# ✅ Let user fill out form before verifying token
with st.form("reset_password_form"):
    new_password = st.text_input("New password", type="password")
    confirm_password = st.text_input("Confirm password", type="password")
    submitted = st.form_submit_button("Reset Password")

    if submitted:
        if new_password != confirm_password:
            st.error("❌ Passwords do not match.")
            st.stop()

        # ✅ Now verify the token and decode it
        if not verify_token(token):
            st.error("❌ The reset link is invalid or expired.")
            st.stop()

        email = get_email_from_token(token)
        if not email:
            st.error("❌ Failed to extract email from token.")
            st.stop()

        update_user_password(email, new_password)
        st.success("✅ Password successfully updated! You can now log in.")
        st.balloons()
