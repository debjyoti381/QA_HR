import os
import streamlit as st
from dotenv import load_dotenv

# Load environment variables from .env
load_dotenv()

# Function to mask sensitive values
def mask_value(value):
    if value:
        return value[:4] + "..." + value[-4:]  # Show only the first and last 4 characters
    return "Not Found"

# Retrieve environment variables
project_id = os.getenv("GOOGLE_PROJECT_ID")
private_key_id = os.getenv("GOOGLE_PRIVATE_KEY_ID")
private_key = os.getenv("GOOGLE_PRIVATE_KEY")
client_email = os.getenv("GOOGLE_CLIENT_EMAIL")
client_id = os.getenv("GOOGLE_CLIENT_ID")
client_cert_url = os.getenv("GOOGLE_CLIENT_CERT_URL")
drive_folder_id = os.getenv("GOOGLE_DRIVE_FOLDER_ID")
api_key = os.getenv("GOOGLE_API_KEY")

# Display the variables in Streamlit
st.title("Environment Variables Loaded from .env")
st.write("### Google Project Information")
st.write("**GOOGLE_PROJECT_ID:**", project_id)
st.write("**GOOGLE_PRIVATE_KEY_ID:**", private_key_id)
st.write("**GOOGLE_PRIVATE_KEY:**", mask_value(private_key))
st.write("**GOOGLE_CLIENT_EMAIL:**", client_email)
st.write("**GOOGLE_CLIENT_ID:**", client_id)
st.write("**GOOGLE_CLIENT_CERT_URL:**", client_cert_url)

st.write("### Additional Settings")
st.write("**GOOGLE_DRIVE_FOLDER_ID:**", drive_folder_id)
st.write("**GOOGLE_API_KEY:**", mask_value(api_key))
