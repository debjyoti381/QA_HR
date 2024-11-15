import os

# Access secrets as environment variables
project_id = os.getenv("GOOGLE_PROJECT_ID")
private_key_id = os.getenv("GOOGLE_PRIVATE_KEY_ID")
private_key = os.getenv("GOOGLE_PRIVATE_KEY")
client_email = os.getenv("GOOGLE_CLIENT_EMAIL")
client_id = os.getenv("GOOGLE_CLIENT_ID")
client_cert_url = os.getenv("GOOGLE_CLIENT_CERT_URL")
drive_folder_id = os.getenv("GOOGLE_DRIVE_FOLDER_ID")
api_key = os.getenv("GOOGLE_API_KEY")

# Use the secrets as needed in your application
print("Google Project ID:", project_id)
print("Google Private Key ID:", private_key_id)
print("Google Client Email:", client_email)
# Do not print sensitive information like private keys in production
