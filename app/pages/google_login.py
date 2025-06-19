# app/pages/google_login.py
import os
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))
import streamlit as st
from dotenv import load_dotenv
from backend.oauth import (
    get_flow,
    get_auth_flow,
    get_credentials_from_code,
    refresh_credentials
)
from backend.auth import store_oauth_credentials

load_dotenv()

REDIRECT_URI = st.secrets.get("OAUTH_REDIRECT_URI", "https://youtufy-one.streamlit.app/main")

st.set_page_config(page_title="Google Login – YouTufy", layout="centered")

# Handle OAuth callback (code param)
code = st.query_params.get("code", None)
if code and not st.session_state.get("authenticated"):
    try:
        st.info("🔁 Completing Google login...")

        creds = get_credentials_from_code(code, REDIRECT_URI)
        user_email = creds.id_token.get("email")

        if not user_email:
            st.error("❌ Failed to get user email from Google.")
            st.stop()

        st.session_state["user"] = user_email
        st.session_state["username"] = user_email.split("@")[0]
        st.session_state["google_creds"] = creds.to_json()
        st.session_state["authenticated"] = True

        store_oauth_credentials(creds, user_email)

        st.success(f"✅ Logged in as {user_email}. Redirecting...")
        st.switch_page("main")

    except Exception as e:
        st.error("❌ OAuth token exchange failed.")
        st.exception(e)
        st.stop()

# Not a callback, show login button
else:
    flow = get_flow(REDIRECT_URI)
    auth_url, _ = flow.authorization_url(prompt="consent", access_type="offline")

    st.markdown(f"""
        <p style="text-align:center; margin-top: 40px;">
            <a href="{auth_url}" style="
                padding: 14px 24px;
                background-color: #8F00FF;
                color: white;
                text-decoration: none;
                border-radius: 6px;
                font-weight: bold;
                font-size: 1rem;">
                🔐 Sign in with Google
            </a>
        </p>
    """, unsafe_allow_html=True)
