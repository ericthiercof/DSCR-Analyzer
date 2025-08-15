
import requests

try:
    response = requests.get("http://localhost:8000/")
    print(f"Status code: {response.status_code}")
    print(f"Response: {response.json()}")
    print("✅ API is accessible")
except Exception as e:
    print(f"❌ Error: {e}")

