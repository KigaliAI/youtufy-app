# app/main.py
import streamlit as st
import sys, os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from controllers.dashboard import load_dashboard

st.set_page_config(page_title="YouTufy", layout="wide")

user_email = st.session_state.get("user")
username = st.session_state.get("username")

# Loads dashboard if user is authenticated
if user_email:
    load_dashboard(user_email, username)
else:
    st.warning("🔒 Please sign in to access your subscriptions via the login options on the homepage.")
