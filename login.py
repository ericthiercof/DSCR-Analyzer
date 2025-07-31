__all__ = ["login_screen"]
import streamlit as st
from firebase_admin import credentials, firestore, initialize_app
import os

# Load Firebase credentials from secrets
cred = credentials.Certificate({
    "type": "service_account",
    "project_id": st.secrets["firebase"]["project_id"],
    "private_key_id": st.secrets["firebase"]["private_key_id"],
    "private_key": st.secrets["firebase"]["private_key"].replace('\\n', '\n'),
    "client_email": st.secrets["firebase"]["client_email"],
    "client_id": st.secrets["firebase"]["client_id"],
    "auth_uri": st.secrets["firebase"]["auth_uri"],
    "token_uri": st.secrets["firebase"]["token_uri"],
    "auth_provider_x509_cert_url": st.secrets["firebase"]["auth_provider_x509_cert_url"],
    "client_x509_cert_url": st.secrets["firebase"]["client_x509_cert_url"]
})

# Only initialize Firebase once
if not hasattr(st.session_state, "firebase_initialized"):
    initialize_app(cred)
    st.session_state.firebase_initialized = True

db = firestore.client()

def login_screen():
    st.title("🔐 Login to DSCR Analyzer")

    username = st.text_input("Username (email)")
    password = st.text_input("Password", type="password")

    if st.button("Login"):
        users_ref = db.collection("users")
        query = users_ref.where("username", "==", username).limit(1).stream()
        user_doc = next(query, None)

        if user_doc:
            user_data = user_doc.to_dict()
            if user_data.get("password") == password:
                st.session_state.logged_in = True
                st.session_state.username = username
                st.success("Logged in successfully!")
            else:
                st.error("Incorrect password.")
        else:
            st.error("User not found.")
