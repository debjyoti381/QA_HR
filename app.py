import os
import streamlit as st

# Load secrets directly from environment variables
project_id = os.getenv("GOOGLE_PROJECT_ID")
private_key_id = os.getenv("GOOGLE_PRIVATE_KEY_ID")
private_key = os.getenv("GOOGLE_PRIVATE_KEY")
client_email = os.getenv("GOOGLE_CLIENT_EMAIL")
client_id = os.getenv("GOOGLE_CLIENT_ID")
client_cert_url = os.getenv("GOOGLE_CLIENT_CERT_URL")
drive_folder_id = os.getenv("GOOGLE_DRIVE_FOLDER_ID")
api_key = os.getenv("GOOGLE_API_KEY")

# Display the loaded secrets (for debugging purposes only)
st.write("Google Project Information")
st.write(f"GOOGLE_PROJECT_ID: {project_id}")
st.write(f"GOOGLE_PRIVATE_KEY_ID: {private_key_id}")
st.write(f"GOOGLE_PRIVATE_KEY: {private_key}")
st.write(f"GOOGLE_CLIENT_EMAIL: {client_email}")
st.write(f"GOOGLE_CLIENT_ID: {client_id}")
st.write(f"GOOGLE_CLIENT_CERT_URL: {client_cert_url}")
st.write("Additional Settings")
st.write(f"GOOGLE_DRIVE_FOLDER_ID: {drive_folder_id}")
st.write(f"GOOGLE_API_KEY: {api_key}")
