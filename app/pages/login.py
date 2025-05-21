import os
import tempfile
import streamlit as st
from google_auth_oauthlib.flow import Flow
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request

# ✅ Config
SCOPES = ['https://www.googleapis.com/auth/youtube.readonly']
st.set_page_config(page_title="Google Login", layout="centered")
st.title("🔐 Sign in to YouTufy with Google")

# ✅ Load client secret
if "GOOGLE_CLIENT_SECRET_JSON" in st.secrets:
    json_data = st.secrets["GOOGLE_CLIENT_SECRET_JSON"]
    temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".json", mode="w")
    temp_file.write(json_data)
    temp_file.close()
    CLIENT_SECRET_PATH = temp_file.name
else:
    CLIENT_SECRET_PATH = "config/client_secret.json"

REDIRECT_URI = st.secrets.get("OAUTH_REDIRECT_URI", "http://localhost:8501/")

# ✅ Get code from URL
code = st.query_params.get("code")

if code:
    try:
        # ✅ OAuth callback: exchange code for credentials
        flow = Flow.from_client_secrets_file(
            CLIENT_SECRET_PATH,
            scopes=SCOPES,
            redirect_uri=REDIRECT_URI
        )
        flow.fetch_token(code=code)
        creds = flow.credentials

        # ✅ Extract user info
        user_email = creds.id_token.get("email", None)
        if not user_email:
            st.error("❌ Failed to retrieve email from Google.")
            st.stop()

        # ✅ Store session info
        st.session_state["user"] = user_email
        st.session_state["username"] = user_email.split("@")[0]

        st.success(f"✅ Logged in as {user_email}")
        st.switch_page("main.py")

    except Exception as e:
        st.error("❌ Failed to complete Google authentication.")
        st.exception(e)
        st.stop()
else:
    # ✅ First-time login: build login URL
    flow = Flow.from_client_secrets_file(
        CLIENT_SECRET_PATH,
        scopes=SCOPES,
        redirect_uri=REDIRECT_URI
    )
    auth_url, _ = flow.authorization_url(prompt='consent', access_type='offline')

    st.markdown("""
        🎥 <strong>YouTufy</strong> securely accesses your YouTube subscriptions.<br>
        🛡️ We request <code>youtube.readonly</code> permission.<br>
        ✅ Click below to continue with Google.
    """, unsafe_allow_html=True)

    st.markdown(f"""
        <p style="text-align:center; margin-top: 20px;">
            <a href="{auth_url}" style="
                padding: 14px 24px;
                background-color: #8F00FF;
                color: white;
                text-decoration: none;
                border-radius: 6px;
                font-weight: bold;">
                🔐 Sign in with Google
            </a>
        </p>
    """, unsafe_allow_html=True)
