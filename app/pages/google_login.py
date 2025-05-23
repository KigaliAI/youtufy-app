import os
import tempfile
import streamlit as st
from google_auth_oauthlib.flow import Flow
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from backend.auth import store_oauth_credentials  # ✅ Ensure OAuth tokens are stored properly

# ✅ Set page config
st.set_page_config(page_title="Google Login", layout="centered")
st.title("🔐 Sign in to YouTufy with Google")

SCOPES = ['https://www.googleapis.com/auth/youtube.readonly']

# ✅ Always use production URI for Streamlit Cloud
oauth_redirect_uri = "https://youtufy-one.streamlit.app/"

# ✅ Load client secret
if "GOOGLE_CLIENT_SECRET_JSON" in st.secrets:
    json_data = st.secrets["GOOGLE_CLIENT_SECRET_JSON"]
    temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".json", mode="w")
    temp_file.write(json_data)
    temp_file.close()
    CLIENT_SECRET_PATH = temp_file.name
else:
    st.error("❌ No Google client secret found.")
    st.stop()

# ✅ Retrieve OAuth authorization code
code = st.query_params.get("code")

if code:
    try:
        flow = Flow.from_client_secrets_file(
            CLIENT_SECRET_PATH,
            scopes=SCOPES,
            redirect_uri=oauth_redirect_uri
        )
        flow.fetch_token(code=code)
        creds = flow.credentials
        user_email = creds.id_token.get("email")

        if not user_email:
            st.error("❌ Could not retrieve user email from token.")
            st.stop()

        # ✅ Store OAuth credentials properly
        st.session_state["user"] = user_email
        st.session_state["username"] = user_email.split("@")[0]
        store_oauth_credentials(creds)  # ✅ Ensures token persistence

        st.success(f"✅ Logged in as {user_email}")
        st.switch_page("pages/youtube_subscriptions.py")  # ✅ Redirect to subscriptions page

    except Exception as e:
        st.error("❌ Google OAuth failed.")
        st.exception(e)
        st.stop()
else:
    flow = Flow.from_client_secrets_file(
        CLIENT_SECRET_PATH,
        scopes=SCOPES,
        redirect_uri=oauth_redirect_uri
    )
    auth_url, _ = flow.authorization_url(prompt='consent', access_type='offline')

    st.markdown("""
        👉 <strong>YouTufy</strong> securely accesses your YouTube subscriptions.<br>
        👉 We request <code>youtube.readonly</code> permission.<br>
        👉 Click below to continue with Google.
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
