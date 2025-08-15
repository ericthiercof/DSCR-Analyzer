import requests
import os
from typing import List, Dict

ZILLOW_API_KEY = os.getenv("ZILLOW_API_KEY")
ZILLOW_API_HOST = os.getenv("ZILLOW_API_HOST")

def fetch_properties(city: str, state: str, max_results: int = 50) -> List[Dict]:
    """Fetch properties from Zillow API with bed and bath counts."""
    if not ZILLOW_API_KEY:
        print("⚠️ Zillow API key not found")
        return []
        
    url = "https://zillow-com1.p.rapidapi.com/propertyExtendedSearch"
    headers = {
        "X-RapidAPI-Key": ZILLOW_API_KEY,
        "X-RapidAPI-Host": ZILLOW_API_HOST
    }
    params = {
        "location": f"{city}, {state}",
        "status_type": "ForSale",
        "home_type": "Houses",
        "limit": str(max_results)
    }
    
    try:
        resp = requests.get(url, headers=headers, params=params)
        if resp.status_code != 200:
            print(f"Zillow API error: {resp.status_code} - {resp.text}")
            return []
        
        data = resp.json()
        properties = data.get("props", [])
        print(f"✅ Fetched {len(properties)} properties from Zillow")
        
        formatted_properties = []
        for prop in properties:
            formatted_properties.append({
                "address": prop.get("address"),
                "price": prop.get("price"),
                "bedrooms": prop.get("bedrooms"),
                "bathrooms": prop.get("bathrooms"),
                "zpid": prop.get("zpid"),
                "rentZestimate": prop.get("rentZestimate"),
                "hoaFee": prop.get("hoaFee"),
                "propertyTaxRate": prop.get("propertyTaxRate")
            })
        
        return formatted_properties
    
    except Exception as e:
        print(f"Error fetching properties: {e}")
        return []