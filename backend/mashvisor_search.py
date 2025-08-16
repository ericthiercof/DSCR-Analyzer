import re 
import requests
import os
from typing import List, Dict
import math

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
    
    # Helper methods for location-based neighborhood selection
    def _calculate_distance(self, lat1, lon1, lat2, lon2):
        """Calculate distance between two coordinates using Haversine formula (in miles)"""
        if not all([lat1, lon1, lat2, lon2]):
            return float('inf')
        
        # Convert to radians
        lat1, lon1, lat2, lon2 = map(math.radians, [lat1, lon1, lat2, lon2])
        
        # Haversine formula
        dlat = lat2 - lat1
        dlon = lon2 - lon1
        a = math.sin(dlat/2)**2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon/2)**2
        c = 2 * math.asin(math.sqrt(a))
        r = 3956  # Radius of earth in miles
        return c * r

    def _find_closest_neighborhoods(self, neighborhoods, zipcode=None, latitude=None, longitude=None):
        """Find neighborhoods closest to the property location"""
        if not neighborhoods:
            return neighborhoods
            
        # If we have coordinates, sort by distance
        if latitude is not None and longitude is not None:
            print(f"🎯 Sorting neighborhoods by distance from coordinates ({latitude}, {longitude})")
            
            # Calculate distance to each neighborhood
            for hood in neighborhoods:
                hood_lat = hood.get('latitude')
                hood_lon = hood.get('longitude')
                distance = self._calculate_distance(latitude, longitude, hood_lat, hood_lon)
                hood['distance_miles'] = distance
            
            # Sort by distance (closest first)
            neighborhoods.sort(key=lambda x: x.get('distance_miles', float('inf')))
            
            # Log the sorted neighborhoods
            for i, hood in enumerate(neighborhoods[:5]):  # Show top 5
                print(f"  {i+1}. {hood.get('name')} - {hood.get('distance_miles', 'N/A'):.2f} miles")
            
            return neighborhoods
        
        # If we have zipcode but no coordinates, try to match by name/proximity
        # This is a fallback - in a real implementation you'd want to geocode the zipcode
        if zipcode:
            print(f"🎯 Attempting to find neighborhood for zipcode {zipcode}")
            # For now, just return neighborhoods as-is since we don't have zipcode->coordinate mapping
            # In production, you'd want to use a geocoding service here
        
        return neighborhoods

    # Methods specifically for rental comps functionality
    def get_property_comps(self, city, state, zipcode, bedrooms=None, bathrooms=None, latitude=None, longitude=None):
        """Get rental comps for a property prioritizing by location"""
        try:
            print(f"🔍 Getting location-specific comps for {city}, {state}, zip: {zipcode}")
            if latitude and longitude:
                print(f"📍 Property coordinates: ({latitude}, {longitude})")
            
            # Get all neighborhoods for this city
            neighborhoods = self.get_city_neighborhoods(state, city)
            
            if not neighborhoods or len(neighborhoods) == 0:
                print(f"❌ No neighborhoods found for {city}, {state}")
                return []
                
            print(f"✅ Found {len(neighborhoods)} neighborhoods in {city}, {state}")
            
            # Sort neighborhoods by proximity to the property location
            sorted_neighborhoods = self._find_closest_neighborhoods(
                neighborhoods.copy(), zipcode, latitude, longitude
            )
            
            # Limit neighborhood checks to avoid API overload, but prioritize closest ones
            max_neighborhoods_to_check = 4
            all_comps = []
            
            for i, hood in enumerate(sorted_neighborhoods):
                if i >= max_neighborhoods_to_check:
                    break
                    
                hood_id = hood.get("id")
                hood_name = hood.get("name")
                distance = hood.get("distance_miles")
                
                if not hood_id:
                    continue
                
                distance_info = f" ({distance:.2f} miles away)" if distance is not None else ""
                print(f"🔍 Checking for rental comps in {hood_name} (ID: {hood_id}){distance_info}")
                
                # Get rental listings for this neighborhood
                hood_comps = self._get_traditional_listings_by_neighborhood(hood_id, state, bedrooms)
                
                if hood_comps and len(hood_comps) > 0:
                    print(f"✅ Found {len(hood_comps)} comps in {hood_name}")
                    
                    # Tag these comps with their neighborhood name and distance
                    for comp in hood_comps:
                        comp["neighborhood"] = hood_name
                        if distance is not None:
                            comp["neighborhood_distance_miles"] = round(distance, 2)
                        
                    all_comps.extend(hood_comps)
                    
                    # If we have enough comps, stop searching
                    if len(all_comps) >= 10:
                        break
            
            if all_comps:
                print(f"✅ Returning {len(all_comps)} rental comps from {len(set(comp.get('neighborhood') for comp in all_comps))} neighborhoods")
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