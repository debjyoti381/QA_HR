import os

def load_and_print_env_vars():
    project_id = os.getenv("GOOGLE_PROJECT_ID")
    private_key_id = os.getenv("GOOGLE_PRIVATE_KEY_ID")
    private_key = os.getenv("GOOGLE_PRIVATE_KEY")
    client_email = os.getenv("GOOGLE_CLIENT_EMAIL")
    client_id = os.getenv("GOOGLE_CLIENT_ID")
    client_cert_url = os.getenv("GOOGLE_CLIENT_CERT_URL")
    drive_folder_id = os.getenv("GOOGLE_DRIVE_FOLDER_ID")
    api_key = os.getenv("GOOGLE_API_KEY")

    # Check each variable to confirm it was loaded, with a fallback message if not
    print("Environment Variables Loaded from GitHub Secrets")
    print("Google Project Information")
    print("GOOGLE_PROJECT_ID:", project_id or "Not loaded")
    print("GOOGLE_PRIVATE_KEY_ID:", private_key_id or "Not loaded")
    print("GOOGLE_PRIVATE_KEY:", private_key[:50] + '...' if private_key else "Not loaded")  # Truncate for security
    print("GOOGLE_CLIENT_EMAIL:", client_email or "Not loaded")
    print("GOOGLE_CLIENT_ID:", client_id or "Not loaded")
    print("GOOGLE_CLIENT_CERT_URL:", client_cert_url or "Not loaded")

    print("\nAdditional Settings")
    print("GOOGLE_DRIVE_FOLDER_ID:", drive_folder_id or "Not loaded")
    print("GOOGLE_API_KEY:", api_key or "Not loaded")

if __name__ == "__main__":
    load_and_print_env_vars()
