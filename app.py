import os
import streamlit as st
from dotenv import load_dotenv

# Load environment variables explicitly from a .env file
dotenv_path = ".env"  # Specify the relative or absolute path to your .env file if needed
load_dotenv(dotenv_path)

# Retrieve environment variables and handle missing values
project_id = os.getenv("GOOGLE_PROJECT_ID", "Not Found")
private_key_id = os.getenv("GOOGLE_PRIVATE_KEY_ID", "Not Found")
private_key = os.getenv("GOOGLE_PRIVATE_KEY", "Not Found")
client_email = os.getenv("GOOGLE_CLIENT_EMAIL", "Not Found")
client_id = os.getenv("GOOGLE_CLIENT_ID", "Not Found")
client_cert_url = os.getenv("GOOGLE_CLIENT_CERT_URL", "Not Found")
drive_folder_id = os.getenv("GOOGLE_DRIVE_FOLDER_ID", "Not Found")
api_key = os.getenv("GOOGLE_API_KEY", "Not Found")

# Display the variables in Streamlit
st.title("Environment Variables Loaded from .env")
st.write("### Google Project Information")
st.write("**GOOGLE_PROJECT_ID:**", project_id)
st.write("**GOOGLE_PRIVATE_KEY_ID:**", private_key_id)
st.write("**GOOGLE_PRIVATE_KEY:**", private_key)
st.write("**GOOGLE_CLIENT_EMAIL:**", client_email)
st.write("**GOOGLE_CLIENT_ID:**", client_id)
st.write("**GOOGLE_CLIENT_CERT_URL:**", client_cert_url)

st.write("### Additional Settings")
st.write("**GOOGLE_DRIVE_FOLDER_ID:**", drive_folder_id)
st.write("**GOOGLE_API_KEY:**", api_key)

# Check if variables were loaded successfully
if "Not Found" in [project_id, private_key_id, private_key, client_email, client_id, client_cert_url, drive_folder_id, api_key]:
    st.warning("Some environment variables were not loaded. Check .env file and paths.")
else:
    st.success("All environment variables loaded successfully!")
