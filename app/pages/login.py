import os
import tempfile
import streamlit as st
from google_auth_oauthlib.flow import Flow

SCOPES = ['https://www.googleapis.com/auth/youtube.readonly']
st.set_page_config(page_title="Google Login", layout="centered")
st.title("🔐 Sign in to YouTufy with Google")

# ✅ Always use your deployed domain
REDIRECT_URI = "https://youtufy-one.streamlit.app/"

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

code = st.query_params.get("code")

if code:
    try:
        flow = Flow.from_client_secrets_file(
            CLIENT_SECRET_PATH,
            scopes=SCOPES,
            redirect_uri=REDIRECT_URI
        )
        flow.fetch_token(code=code)
        creds = flow.credentials
        user_email = creds.id_token.get("email", None)

        if not user_email:
            st.error("❌ Could not extract email from token.")
            st.stop()

        st.session_state["user"] = user_email
        st.session_state["username"] = user_email.split("@")[0]
        st.success(f"✅ Logged in as {user_email}")
        st.switch_page("main.py")

    except Exception as e:
        st.error("❌ Failed to complete Google authentication.")
        st.exception(e)
else:
    flow = Flow.from_client_secrets_file(
        CLIENT_SECRET_PATH,
        scopes=SCOPES,
        redirect_uri=REDIRECT_URI
    )
    auth_url, _ = flow.authorization_url(prompt='consent', access_type='offline')

    st.markdown("Click below to sign in with your Google account:")
    st.markdown(f"""
        <p style="text-align:center;">
            <a href="{auth_url}" style="padding: 12px 24px; background: #8F00FF; color: white; border-radius: 6px; text-decoration: none;">🔐 Sign in with Google</a>
        </p>
    """, unsafe_allow_html=True)
