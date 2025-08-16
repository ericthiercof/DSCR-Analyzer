## Key Files Content
### Backend Entry Point (main.py)
```python
"""
FastAPI backend for Real Estate Investment Analysis app
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import os
from dotenv import load_dotenv, find_dotenv
import time
import json
from typing import Dict

# Load environment variables from .env file
dotenv_path = find_dotenv()
if dotenv_path:
    load_dotenv(dotenv_path)
    print(f"🔍 Debug: .env file found at: {dotenv_path}")

# Import Firebase utilities
from backend.utils.firebase import initialize_firebase

# Initialize Firebase
initialize_firebase()

# Import routes
from backend.routes import property_router, user_router
# Import the property_analysis_router when ready to use it
# from backend.routes.property_analysis import router as property_analysis_router

# Create FastAPI app
app = FastAPI(
    title="DSCR Property Analyzer API",
    description="API for real estate investment property analysis",
    version="1.0.0",
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods
    allow_headers=["*"],  # Allows all headers
)

# Include routers
app.include_router(property_router, prefix="/api", tags=["property"])
app.include_router(user_router, prefix="/api", tags=["users"])
# Include the property_analysis_router when ready to use it
# app.include_router(property_analysis_router, prefix="/api", tags=["analysis"])

@app.get("/", tags=["health"])
async def health_check() -> Dict:
    """Health check endpoint."""
    return {"status": "ok", "timestamp": time.time()}

# Run the app
if __name__ == "__main__":
    import uvicorn
    print("🚀 Starting your DSCR Property Analyzer API...")
    print("📚 API Documentation: http://localhost:8000/docs")
    print("🌐 API Health Check: http://localhost:8000")
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
```
### Property Routes
```python
from fastapi import APIRouter, HTTPException
from typing import List, Dict
import os

from ..models.search import SearchRequest
from ..models.property import PropertyResult
from ..services.zillow import fetch_properties
from ..services.finance import estimate_mortgage_payment
from ..services.serpapi import fetch_average_rent_serpapi
from backend.mashvisor_search import mashvisor_search, create_listing_urls

router = APIRouter()

# Add this at the module level to store cached neighborhoods
city_neighborhoods_cache = {}

@router.post("/search", response_model=List[PropertyResult])
async def search_properties(request: SearchRequest):
    """
    Search for investment properties using Zillow API
    """
    try:
        print(f"🔍 Searching for properties in {request.city}, {request.state}")
        
        # Fetch properties using your function
        properties = fetch_properties(request.city, request.state)
        
        if not properties:
            return []
        
        results = []
        fallback_rent = {}
        
        for prop in properties:
            price = prop.get("price")
            address = prop.get("address")
            rent_zestimate = prop.get("rentZestimate")
            bedrooms = prop.get("bedrooms")
            bathrooms = prop.get("bathrooms")
            zpid = prop.get("zpid")
            zipcode = address.split()[-1] if address else None
            hoa_fee = prop.get("hoaFee") or prop.get("priceComponent", {}).get("hoa") or 0
            tax_rate = prop.get("propertyTaxRate") or 0.0125

            # Validation
            if not (price and address and bedrooms and zipcode and zpid):
                continue
            if int(price) < int(request.min_price) or int(request.max_price) > 0 and int(price) > int(request.max_price):
                continue

            # Calculate mortgage payment
            monthly_payment = estimate_mortgage_payment(
                price, 
                request.down_payment / 100, 
                request.interest_rate, 
                tax_rate=tax_rate, 
                hoa_fee=hoa_fee
            )

            # Determine rent
            rent = rent_zestimate or fallback_rent.get(f"{zipcode}-{bedrooms}")
            rent_type = "Zestimate" if rent_zestimate else "Unknown"

            # Fallback to SerpAPI
            if not rent:
                fallback_rent_value = fetch_average_rent_serpapi(zipcode, bedrooms)
                if fallback_rent_value:
                    rent = fallback_rent_value
                    rent_type = "Market Average"
                    fallback_rent[f"{zipcode}-{bedrooms}"] = rent

            # Calculate DSCR
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
                    insurance_cost=round(price * 0.0035 / 12, 2),
                    bedrooms=bedrooms,
                    bathrooms=bathrooms
                )
                
                results.append(result)
        
        sorted_results = sorted(results, key=lambda x: x.dscr, reverse=True)
        print(f"✅ Processed {len(sorted_results)} qualifying properties")
        return sorted_results
        
    except Exception as e:
        print(f"❌ Search error: {e}")
        raise HTTPException(status_code=500, detail=f"Search failed: {str(e)}")

@router.post("/property-comps")
async def get_property_comps(property_data: dict):
    """Get rental comps for a property with location-based prioritization"""
    try:
        address = property_data.get("address", "")
        city = property_data.get("city", "")
        state = property_data.get("state", "")
        zipcode = property_data.get("zip", "")
        bedrooms = property_data.get("bedrooms")
        bathrooms = property_data.get("bathrooms")
        
        # Get coordinates for location-based prioritization
        latitude = property_data.get("latitude")
        longitude = property_data.get("longitude")
        
        print(f"🔍 Looking for rental comps in {city}, {state}, {zipcode}")
        
        # Use the new location-aware comps method
        comps = mashvisor_search.get_property_comps(
            city=city,
            state=state,
            zipcode=zipcode,
            bedrooms=bedrooms,
            bathrooms=bathrooms,
            latitude=latitude,
            longitude=longitude
        )
        
        if comps and len(comps) > 0:
            return comps
        else:
            # Fall back to the original method if needed
            print("⚠️ No location-specific comps found, falling back to general search")
            neighborhoods = mashvisor_search.get_city_neighborhoods(state, city)
            if neighborhoods:
                # Use existing neighborhood search as fallback
                pass
            return []
            
    except Exception as e:
        print(f"❌ Error getting property comps: {str(e)}")
        return []

@router.post("/search-with-cache")
async def search_properties_with_cache(search_data: Dict):
    """Search for real estate properties and cache neighborhood data"""
    try:
        # Extract search parameters
        location = search_data.get('location', '')
        price_min = search_data.get('price_min', 0)
        price_max = search_data.get('price_max', 0)
        
        # Define the properties variable before using it
        # Use your existing fetch_properties function or similar
        city = location.split(',')[0].strip() if ',' in location else location
        state = location.split(',')[1].strip() if ',' in location else ''
        properties = fetch_properties(city, state)  # This should match how you fetch properties
        
        # If search was successful, try to cache neighborhood data
        if properties and len(properties) > 0:
            # Extract city and state from first property
            first_property = properties[0]
            city = first_property.get('city', '') or city
            state = first_property.get('state', '') or state
            
            # Create cache key
            cache_key = f"{city.lower()},{state.lower()}"
            
            # Check if we already have this city's neighborhoods
            if cache_key not in city_neighborhoods_cache:
                print(f"🏙️ Caching neighborhoods for {city}, {state}")
                neighborhoods = mashvisor_search.get_city_neighborhoods(state, city)
                
                if neighborhoods and len(neighborhoods) > 0:
                    city_neighborhoods_cache[cache_key] = neighborhoods
                    print(f"✅ Cached {len(neighborhoods)} neighborhoods for {city}, {state}")
                else:
                    print(f"⚠️ No neighborhoods found to cache for {city}, {state}")
            else:
                print(f"ℹ️ Using cached neighborhoods for {city}, {state}")
        
        return properties
        
    except Exception as e:
        # Proper error handling with actual code
        print(f"❌ Error searching properties: {str(e)}")
        return []  # Return empty list on error```
### Mashvisor Integration
```python
import re 
import requests
import os
from typing import List, Dict

class MashvisorPropertySearch:
    def __init__(self):
        self.api_key = os.getenv('MASHVISOR_API_KEY')
        print(f"🔑 Loaded Mashvisor API Key: {self.api_key}")
        if not self.api_key:
            raise ValueError("Mashvisor API key not found. Please check your .env file.")
        
        # Set base URL and headers
        self.base_url = "https://api.mashvisor.com/v1.1"
        self.headers = {
            "x-api-key": self.api_key,
            "Content-Type": "application/json"
        }
    
    # Methods specifically for rental comps functionality
    def get_property_comps(self, city, state, zipcode, bedrooms=None, bathrooms=None, latitude=None, longitude=None):
        """Get rental comps for a property prioritizing by location"""
        try:
            print(f"🔍 Getting location-specific comps for {city}, {state}, zip: {zipcode}")
            
            # Get all neighborhoods for this city
            neighborhoods = self.get_city_neighborhoods(state, city)
            
            if not neighborhoods or len(neighborhoods) == 0:
                print(f"❌ No neighborhoods found for {city}, {state}")
                return []
                
            print(f"✅ Found {len(neighborhoods)} neighborhoods in {city}, {state}")
            
            # Limit neighborhood checks to avoid API overload
            max_neighborhoods_to_check = 4
            all_comps = []
            
            for i, hood in enumerate(neighborhoods):
                if i >= max_neighborhoods_to_check:
                    break
                    
                hood_id = hood.get("id")
                hood_name = hood.get("name")
                
                if not hood_id:
                    continue
                    
                print(f"🔍 Checking for rental comps in {hood_name} (ID: {hood_id})")
                
                # Get rental listings for this neighborhood
                hood_comps = self._get_traditional_listings_by_neighborhood(hood_id, state, bedrooms)
                
                if hood_comps and len(hood_comps) > 0:
                    print(f"✅ Found {len(hood_comps)} comps in {hood_name}")
                    
                    # Tag these comps with their neighborhood name
                    for comp in hood_comps:
                        comp["neighborhood"] = hood_name
                        
                    all_comps.extend(hood_comps)
                    
                    # If we have enough comps, stop searching
                    if len(all_comps) >= 10:
                        break
            
            if all_comps:
                print(f"✅ Returning {len(all_comps)} rental comps from neighborhoods")
                return all_comps
            else:
                print("⚠️ No rental comps found in any neighborhood")
                return []
                
        except Exception as e:
            print(f"❌ Error getting property rental comps: {str(e)}")
            import traceback
            traceback.print_exc()
            return []
    
    def get_city_neighborhoods(self, state, city):
        """Get all neighborhood IDs for a city"""
        try:
            # URL encode the city name (spaces become %20)
            encoded_city = city.replace(' ', '%20')
            endpoint = f"{self.base_url}/client/city/neighborhoods/{state}/{encoded_city}"
            
            print(f"🔍 Fetching neighborhoods for {city}, {state}")
            response = requests.get(endpoint, headers=self.headers, timeout=30)
            
            print(f"📡 Request URL: {endpoint}")
            print(f"📊 Response status: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                
                if data.get("status") == "success" and data.get("content") and data["content"].get("results"):
                    neighborhoods = data["content"]["results"]
                    print(f"✅ Found {len(neighborhoods)} neighborhoods in {city}, {state}")
                    
                    # Extract neighborhood IDs and names
                    neighborhood_data = []
                    for hood in neighborhoods:
                        neighborhood_data.append({
                            "id": hood.get("id"),
                            "name": hood.get("name"),
                            "latitude": hood.get("latitude"),
                            "longitude": hood.get("longitude")
                        })
                    
                    return neighborhood_data
                else:
                    print(f"⚠️ No neighborhoods found or unexpected response format")
                    return []
            else:
                print(f"❌ Error fetching neighborhoods: {response.status_code}")
                return []
                
        except Exception as e:
            print(f"❌ Exception fetching city neighborhoods: {str(e)}")
            return []
    
    def _get_traditional_listings_by_neighborhood(self, neighborhood_id, state, bedrooms=None):
        """Get traditional rental listings for a specific neighborhood"""
        try:
            endpoint = f"{self.base_url}/client/neighborhood/{neighborhood_id}/traditional/listing"
            
            # Create parameters with required fields
            params = {
                "format": "json",
                "state": state
            }
            
            # Try different parameters to get results
            if bedrooms:
                params["category"] = bedrooms
                
            # Let's try without the bedrooms filter first
            params.pop("category", None)
            
            print(f"🔍 Fetching traditional rental listings for neighborhood ID: {neighborhood_id}")
            response = requests.get(endpoint, headers=self.headers, params=params, timeout=30)
            
            print(f"📡 Request URL: {endpoint}")
            print(f"📊 Response status: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                
                # Debug the entire response structure in more detail
                print(f"📋 Response keys: {list(data.keys())}")
                
                if data.get("status") == "success" and data.get("content"):
                    content = data.get("content", {})
                    
                    # Let's print the full structure of content
                    if isinstance(content, dict):
                        print(f"📋 Content keys: {list(content.keys())}")
                        # If content has a 'content' key, check that too (nested structures)
                        if 'content' in content:
                            print(f"📋 Nested content keys: {list(content['content'].keys())}")
                    elif isinstance(content, list):
                        print(f"📋 Content is a list with {len(content)} items")
                        if content and len(content) > 0:
                            print(f"📋 First item keys: {list(content[0].keys())}")
                    else:
                        print(f"📋 Content type: {type(content)}")
                        print(f"📋 Content value: {content}")
                    
                    # Try different possible structures
                    if isinstance(content, dict):
                        # Try multiple possible keys where listings might be stored
                        for key in ["results", "properties", "listings", "items", "data"]:
                            if key in content:
                                listings = content[key]
                                print(f"✅ Found listings under '{key}' key: {len(listings)}")
                                break
                        else:
                            listings = []
                    elif isinstance(content, list):
                        listings = content
                    else:
                        listings = []
                    
                    print(f"✅ Found {len(listings)} traditional rental listings")
                    
                    # Format the rental comps
                    formatted_comps = []
                    for listing in listings:
                        comp = {
                            "address": listing.get("address", ""),
                            "city": listing.get("city", ""),
                            "state": listing.get("state", ""),
                            "zipcode": listing.get("zipcode", ""),
                            "price": listing.get("price", 0),
                            "rent": listing.get("price", 0),
                            "bedrooms": listing.get("beds", 0),
                            "bathrooms": listing.get("baths", 0),
                            "sqft": listing.get("sqft", 0),
                            "year_built": listing.get("year_built"),
                            "property_type": listing.get("type", ""),
                            "distance": listing.get("distance", 0)
                        }
                        formatted_comps.append(comp)
                    
                    return formatted_comps
                else:
                    print(f"⚠️ No rental listings found in response")
                    return []
            else:
                print(f"⚠️ API returned status code: {response.status_code}")
                return []
                
        except Exception as e:
            print(f"❌ Exception fetching rental listings: {str(e)}")
            return []

# Create an instance that can be imported by other modules
mashvisor_search = MashvisorPropertySearch()

# Create listing URLs function
def create_listing_urls(address: str, city: str, state: str, zip_code: str = None) -> Dict[str, str]:
    """
    Generate URLs for property listings based on the address, city, state, and optional zip code.
    """
    base_url = "https://www.zillow.com/homes/"
    formatted_address = "-".join(address.split())
    formatted_city = "-".join(city.split())
    formatted_state = state
    formatted_zip = f"-{zip_code}" if zip_code else ""
    zillow_url = f"{base_url}{formatted_address}-{formatted_city}-{formatted_state}{formatted_zip}_rb/"
    
    return {"zillow": zillow_url}```
