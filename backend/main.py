"""
FastAPI version of your Streamlit app
All your existing functions and logic preserved
"""

from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
import requests
from math import isclose
import firebase_admin
from firebase_admin import credentials, firestore
from datetime import datetime
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Create FastAPI app
app = FastAPI(
    title="🏘️ DSCR Investment Property Analyzer API",
    description="Your Streamlit app converted to professional API",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure this properly for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize Firebase - Try different initialization methods
if not firebase_admin._apps:
    try:
        # Try to use firebase_key.json if it exists
        if os.path.exists("firebase_key.json"):
            cred = credentials.Certificate("firebase_key.json")
            firebase_admin.initialize_app(cred)
            print("✅ Firebase initialized with firebase_key.json")
        else:
            # Use default credentials (this will work in many cloud environments)
            firebase_admin.initialize_app()
            print("✅ Firebase initialized with default credentials")
    except Exception as e:
        print(f"⚠️ Firebase initialization failed: {e}")
        print("📝 Note: Some features requiring Firebase will not work")

# Try to get database client
try:
    db = firestore.client()
    print("✅ Firestore client initialized")
except Exception as e:
    print(f"⚠️ Firestore client initialization failed: {e}")
    db = None

# Your secrets from .env file
ZILLOW_API_KEY = os.getenv("ZILLOW_API_KEY")
ZILLOW_API_HOST = os.getenv("ZILLOW_API_HOST")
SERPAPI_KEY = os.getenv("SERPAPI_KEY")

print(f"🔑 API Keys loaded: Zillow={'✅' if ZILLOW_API_KEY else '❌'}, SerpAPI={'✅' if SERPAPI_KEY else '❌'}")

# --- YOUR EXACT FUNCTIONS FROM STREAMLIT ---

def estimate_mortgage_payment(price, down_payment_pct=0.20, interest_rate=7.0, term_years=30, tax_rate=0.0125, hoa_fee=0):
    """Your exact mortgage calculation function"""
    loan_amount = price * (1 - down_payment_pct)
    monthly_rate = interest_rate / 100 / 12
    n_payments = term_years * 12

    if isclose(monthly_rate, 0.0):
        base_payment = loan_amount / n_payments
    else:
        base_payment = loan_amount * (monthly_rate * (1 + monthly_rate)**n_payments) / ((1 + monthly_rate)**n_payments - 1)

    property_tax = price * tax_rate / 12
    insurance = price * 0.0035 / 12  # Estimated insurance cost
    pmi = 0
    if down_payment_pct < 0.20:
        pmi = price * 0.005 / 12

    total_payment = base_payment + property_tax + hoa_fee + insurance + pmi
    return round(total_payment, 2)

def fetch_average_rent_serpapi(zipcode, bedrooms):
    """Your exact SerpAPI function"""
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

def fetch_properties(city, state, max_results=50):
    """Your exact Zillow API function"""
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
        return properties
    except Exception as e:
        print(f"Error fetching properties: {e}")
        return []

# --- PYDANTIC MODELS ---

class SearchRequest(BaseModel):
    city: str
    state: str
    down_payment: float
    interest_rate: float
    min_price: int
    max_price: int
    username: str = "api_user"

class PropertyResult(BaseModel):
    address: str
    price: int
    monthly_payment: float
    rent: int
    rent_type: str
    dscr: float
    hoa_fee: float
    tax_rate: float
    zpid: str
    zillow_url: str
    insurance_cost: float

# --- API ENDPOINTS ---

@app.get("/")
async def root():
    return {
        "message": "🏘️ DSCR Investment Property Analyzer API", 
        "status": "running",
        "firebase_connected": db is not None,
        "zillow_api": ZILLOW_API_KEY is not None,
        "serpapi": SERPAPI_KEY is not None
    }

@app.post("/api/search", response_model=List[PropertyResult])
async def search_properties(request: SearchRequest):
    """
    Your exact Streamlit search logic converted to API endpoint
    """
    try:
        print(f"🔍 Searching for properties in {request.city}, {request.state}")
        
        # Fetch properties using your function
        properties = fetch_properties(request.city, request.state)
        
        if not properties:
            return []
        
        results = []
        fallback_rent = {}  # Your session state equivalent
        
        # Your exact processing logic from Streamlit
        for prop in properties:
            price = prop.get("price")
            address = prop.get("address")
            rent_zestimate = prop.get("rentZestimate")
            bedrooms = prop.get("bedrooms")
            zpid = prop.get("zpid")
            zipcode = address.split()[-1] if address else None
            hoa_fee = prop.get("hoaFee") or prop.get("priceComponent", {}).get("hoa") or 0
            tax_rate = prop.get("propertyTaxRate") or 0.0125

            # Your exact validation logic
            if not (price and address and bedrooms and zipcode and zpid):
                continue
            if int(price) < int(request.min_price) or int(request.max_price) > 0 and int(price) > int(request.max_price):
                continue

            # Your exact mortgage calculation
            monthly_payment = estimate_mortgage_payment(
                price, 
                request.down_payment / 100, 
                request.interest_rate, 
                tax_rate=tax_rate, 
                hoa_fee=hoa_fee
            )

            # Your exact rent logic
            rent = rent_zestimate or fallback_rent.get(f"{zipcode}-{bedrooms}")
            rent_type = "Zestimate" if rent_zestimate else "Unknown"

            # Your SerpAPI fallback
            if not rent:
                fallback_rent_value = fetch_average_rent_serpapi(zipcode, bedrooms)
                if fallback_rent_value:
                    rent = fallback_rent_value
                    rent_type = "Market Average"
                    fallback_rent[f"{zipcode}-{bedrooms}"] = rent

            # Your exact DSCR calculation
            if rent:
                dscr = round(rent / monthly_payment, 2)
                
                result = PropertyResult(
                    address=address,
                    price=price,
                    monthly_payment=monthly_payment,
                    rent=rent,
                    rent_type=rent_type,
                    dscr=dscr,
                    hoa_fee=hoa_fee,
                    tax_rate=tax_rate,
                    zpid=zpid,
                    zillow_url=f"https://www.zillow.com/homedetails/{zpid}_zpid/",
                    insurance_cost=round(price * 0.0035 / 12, 2)
                )
                
                results.append(result)
        
        # Your exact sorting logic
        sorted_results = sorted(results, key=lambda x: x.dscr, reverse=True)
        print(f"✅ Processed {len(sorted_results)} qualifying properties")
        return sorted_results
        
    except Exception as e:
        print(f"❌ Search error: {e}")
        raise HTTPException(status_code=500, detail=f"Search failed: {str(e)}")

@app.post("/api/save-search")
async def save_search(request: SearchRequest):
    """Your exact save search logic"""
    if not db:
        raise HTTPException(status_code=503, detail="Firebase not available")
        
    try:
        search_data = {
            "city": request.city,
            "state": request.state,
            "down_payment": request.down_payment,
            "interest_rate": request.interest_rate,
            "min_price": request.min_price,
            "max_price": request.max_price,
            "created_at": datetime.now()
        }
        
        # Your exact Firebase save logic
        db.collection("users").document(request.username).collection("saved_searches").add(search_data)
        
        return {"message": "Search saved successfully!"}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to save search: {str(e)}")

@app.get("/api/saved-searches/{username}")
async def get_saved_searches(username: str):
    """Your exact saved searches logic"""
    if not db:
        raise HTTPException(status_code=503, detail="Firebase not available")
        
    try:
        saved_searches_ref = db.collection("users").document(username).collection("saved_searches")
        searches = []
        
        for s in saved_searches_ref.stream():
            data = s.to_dict()
            data["id"] = s.id
            searches.append(data)
        
        return searches
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch searches: {str(e)}")

@app.post("/api/test-firebase")
async def test_firebase():
    """Your exact Firebase test"""
    if not db:
        raise HTTPException(status_code=503, detail="Firebase not available")
        
    try:
        doc_ref = db.collection("test").add({
            "message": "Hello from FastAPI!",
            "timestamp": datetime.now()
        })
        return {"message": "Successfully wrote to Firebase!", "doc_id": doc_ref[1].id}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Firebase test failed: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    print("🚀 Starting your DSCR Property Analyzer API...")
    print("📚 API Documentation: http://localhost:8000/docs")
    print("🌐 API Health Check: http://localhost:8000")
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)