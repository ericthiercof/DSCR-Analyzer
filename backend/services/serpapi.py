import requests
import os

SERPAPI_KEY = os.getenv("SERPAPI_KEY")

def fetch_average_rent_serpapi(zipcode, bedrooms):
    """Fetch average rent data using SerpAPI."""
    if not SERPAPI_KEY:
        print("⚠️ SerpAPI key not found")
        return None
        
    query = f"average rent for {bedrooms} bedroom home in {zipcode}"
    url = "https://serpapi.com/search.json"
    params = {
        "q": query,
        "api_key": SERPAPI_KEY,
        "hl": "en",
        "gl": "us"
    }
    try:
        resp = requests.get(url, params=params)
        data = resp.json()
        for res in data.get("answer_box", {}).get("snippet_highlighted_words", []):
            digits = ''.join(c for c in res if c.isdigit())
            if digits:
                return int(digits)
    except Exception as e:
        print(f"Error fetching rent from SerpAPI: {e}")
    return None