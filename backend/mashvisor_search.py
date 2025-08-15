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
    
    return {"zillow": zillow_url}