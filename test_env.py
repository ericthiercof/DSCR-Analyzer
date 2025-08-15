from dotenv import load_dotenv, find_dotenv
import os

# Debug: Find the .env file
dotenv_path = find_dotenv()
print(f"🔍 Debug: .env file found at: {dotenv_path}")

# Load the .env file
load_dotenv(dotenv_path=dotenv_path)

# Print the Mashvisor API key
print(f"Mashvisor API Key: {os.getenv('MASHVISOR_API_KEY')}")