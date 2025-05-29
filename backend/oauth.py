import os
import json
import tempfile
import streamlit as st
from google_auth_oauthlib.flow import Flow

SCOPES = ["https://www.googleapis.com/auth/youtube.readonly"]

def get_flow(redirect_uri):
    # Load secrets
    secret_path = st.secrets.get("GOOGLE_CLIENT_SECRET_PATH")
    json_string = st.secrets.get("GOOGLE_CLIENT_SECRET_JSON")

    # 🔍 DEBUG LOGGING
    st.write("🔍 DEBUG: client secret path =", secret_path)
    st.write("🔍 DEBUG: using embedded JSON?" , bool(json_string))

    # Try loading from file if available
    if secret_path and os.path.exists(secret_path):
        st.write("✅ Using client secret from file.")
        return Flow.from_client_secrets_file(secret_path, SCOPES, redirect_uri=redirect_uri)

    # Fallback to embedded JSON
    elif json_string:
        try:
            client_config = json.loads(json_string)
            st.write("✅ Using client secret from embedded JSON.")
            return Flow.from_client_config(client_config, SCOPES, redirect_uri=redirect_uri)
        except Exception as e:
            st.error("❌ Failed to parse embedded JSON.")
            raise e

    # If nothing is found
    raise ValueError("❌ No valid Google client secret found in secrets.toml.")
