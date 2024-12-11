import os
from dotenv import load_dotenv

# Load environment variables from the .env file
load_dotenv()

# Debugging: Print environment variables
print(f"CLIENT_ID: {os.getenv('CLIENT_ID')}")
print(f"CLIENT_SECRET: {os.getenv('CLIENT_SECRET')}")
print(f"REDIRECT_URI: {os.getenv('REDIRECT_URI')}")
