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

    # Enhanced methods for better rental comps functionality
    def _calculate_similarity_score(self, comp, target_property):
        """Calculate similarity score between comp and target property"""
        score = 0.0
        max_score = 100.0
        
        # Bedroom match (25% weight)
        if comp.get('bedrooms') and target_property.get('bedrooms'):
            if comp['bedrooms'] == target_property['bedrooms']:
                score += 25.0
            elif abs(comp['bedrooms'] - target_property['bedrooms']) == 1:
                score += 15.0  # Close match
            elif abs(comp['bedrooms'] - target_property['bedrooms']) == 2:
                score += 5.0   # Somewhat close
        
        # Bathroom match (20% weight)
        if comp.get('bathrooms') and target_property.get('bathrooms'):
            if comp['bathrooms'] == target_property['bathrooms']:
                score += 20.0
            elif abs(comp['bathrooms'] - target_property['bathrooms']) <= 0.5:
                score += 15.0  # Close match
            elif abs(comp['bathrooms'] - target_property['bathrooms']) <= 1.0:
                score += 8.0   # Somewhat close
        
        # Price proximity (20% weight)
        if comp.get('price') and target_property.get('price'):
            comp_price = float(comp['price'])
            target_price = float(target_property['price'])
            if comp_price > 0 and target_price > 0:
                price_diff_pct = abs(comp_price - target_price) / target_price
                if price_diff_pct <= 0.1:  # Within 10%
                    score += 20.0
                elif price_diff_pct <= 0.2:  # Within 20%
                    score += 15.0
                elif price_diff_pct <= 0.3:  # Within 30%
                    score += 10.0
                elif price_diff_pct <= 0.5:  # Within 50%
                    score += 5.0
        
        # Square footage similarity (15% weight)
        if comp.get('sqft') and target_property.get('sqft'):
            comp_sqft = float(comp['sqft'])
            target_sqft = float(target_property['sqft'])
            if comp_sqft > 0 and target_sqft > 0:
                sqft_diff_pct = abs(comp_sqft - target_sqft) / target_sqft
                if sqft_diff_pct <= 0.1:  # Within 10%
                    score += 15.0
                elif sqft_diff_pct <= 0.2:  # Within 20%
                    score += 12.0
                elif sqft_diff_pct <= 0.3:  # Within 30%
                    score += 8.0
                elif sqft_diff_pct <= 0.5:  # Within 50%
                    score += 4.0
        
        # Distance bonus (20% weight) - closer is better
        if comp.get('neighborhood_distance_miles') is not None:
            distance = float(comp['neighborhood_distance_miles'])
            if distance <= 1.0:  # Within 1 mile
                score += 20.0
            elif distance <= 2.0:  # Within 2 miles
                score += 15.0
            elif distance <= 5.0:  # Within 5 miles
                score += 10.0
            elif distance <= 10.0:  # Within 10 miles
                score += 5.0
        else:
            # Default moderate score if no distance available
            score += 10.0
        
        return min(score, max_score)  # Cap at 100%

    def get_long_term_comps_direct(self, city, state, target_property):
        """Get long-term rental comps using the dedicated API endpoint"""
        try:
            endpoint = f"{self.base_url}/client/long-term-comps"
            
            params = {
                "state": state,
                "city": city,
                "format": "json"
            }
            
            # Add price filters if target property price is available
            if target_property.get('price'):
                target_price = float(target_property['price'])
                # Set price range: 50% to 150% of target property price (relaxed for more results)
                params["min_price"] = int(target_price * 0.5)
                params["max_price"] = int(target_price * 1.5)
            
            print(f"🔍 Fetching long-term comps using dedicated endpoint for {city}, {state}")
            print(f"📊 Price filter: {params.get('min_price', 'none')} - {params.get('max_price', 'none')}")
            
            response = requests.get(endpoint, headers=self.headers, params=params, timeout=30)
            
            print(f"📡 Request URL: {endpoint}")
            print(f"📊 Response status: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                
                # Enhanced debugging for API response structure
                print(f"📊 API Response structure: status='{data.get('status')}', has_content={bool(data.get('content'))}")
                if data.get("content"):
                    content = data.get("content", {})
                    if isinstance(content, dict):
                        print(f"📊 Content keys: {list(content.keys())}")
                    else:
                        print(f"📊 Content type: {type(content)}, length: {len(content) if hasattr(content, '__len__') else 'N/A'}")
                
                if data.get("status") == "success" and data.get("content"):
                    content = data.get("content", {})
                    
                    # Parse the response structure
                    comps = []
                    if isinstance(content, dict):
                        # Try different possible keys where comps might be stored
                        for key in ["results", "properties", "listings", "comps", "data"]:
                            if key in content:
                                comps = content[key]
                                print(f"✅ Found comps under '{key}' key: {len(comps)}")
                                break
                        
                        # If no comps found in standard keys, show what's available
                        if not comps and content:
                            print(f"⚠️ No comps found in standard keys. Available keys: {list(content.keys())}")
                            # Check if any values in content are lists that might contain comps
                            for key, value in content.items():
                                if isinstance(value, list):
                                    print(f"📊 Key '{key}' contains list with {len(value)} items")
                                    if value and len(value) > 0:
                                        print(f"📊 Sample item from '{key}': {type(value[0])}")
                                        
                    elif isinstance(content, list):
                        comps = content
                        print(f"✅ Content is direct list with {len(comps)} items")
                    
                    # Format and filter the comps
                    formatted_comps = []
                    for comp in comps:
                        formatted_comp = {
                            "address": comp.get("address", ""),
                            "city": comp.get("city", ""),
                            "state": comp.get("state", ""),
                            "zipcode": comp.get("zipcode", ""),
                            "price": comp.get("price", 0),
                            "rent": comp.get("rent", comp.get("price", 0)),
                            "bedrooms": comp.get("bedrooms", comp.get("beds", 0)),
                            "bathrooms": comp.get("bathrooms", comp.get("baths", 0)),
                            "sqft": comp.get("sqft", 0),
                            "year_built": comp.get("year_built"),
                            "property_type": comp.get("type", comp.get("property_type", "")),
                            "source": "Mashvisor Long-term Comps API"
                        }
                        
                        # Use the standard filtering logic instead of early filtering
                        if self._should_include_comp(formatted_comp, target_property):
                            # Calculate similarity score
                            formatted_comp['similarity_score'] = self._calculate_similarity_score(formatted_comp, target_property)
                            formatted_comps.append(formatted_comp)
                    
                    # Sort by similarity score (highest first)
                    formatted_comps.sort(key=lambda x: x.get('similarity_score', 0), reverse=True)
                    
                    print(f"✅ Returning {len(formatted_comps)} filtered and scored long-term comps")
                    return formatted_comps[:15]  # Return top 15 most similar
                    
                else:
                    print(f"⚠️ No comps found in long-term comps API response")
                    return []
            else:
                print(f"⚠️ Long-term comps API returned status code: {response.status_code}")
                if response.status_code == 401:
                    print("🔑 API key authentication required for long-term comps endpoint")
                return []
                
        except Exception as e:
            print(f"❌ Exception fetching long-term comps: {str(e)}")
            return []

    # Methods specifically for rental comps functionality
    def get_property_comps(self, city, state, zipcode, bedrooms=None, bathrooms=None, latitude=None, longitude=None, price=None):
        """Get rental comps for a property with enhanced filtering and similarity scoring"""
        try:
            print(f"🔍 Getting enhanced comps for {city}, {state}, zip: {zipcode}")
            if latitude and longitude:
                print(f"📍 Property coordinates: ({latitude}, {longitude})")
            if price:
                print(f"💰 Target property price: ${price:,}")
            
            # Create target property object for scoring
            target_property = {
                "city": city,
                "state": state,
                "zipcode": zipcode,
                "bedrooms": bedrooms,
                "bathrooms": bathrooms,
                "latitude": latitude,
                "longitude": longitude,
                "price": price
            }
            
            all_comps = []
            
            # Method 1: Try the dedicated long-term comps API first
            print("🎯 Trying dedicated long-term comps API...")
            long_term_comps = self.get_long_term_comps_direct(city, state, target_property)
            if long_term_comps and len(long_term_comps) > 0:
                all_comps.extend(long_term_comps)
                print(f"✅ Added {len(long_term_comps)} comps from long-term comps API")
            
            # Method 2: Supplement with neighborhood-based search if we need more comps
            if len(all_comps) < 5:  # Reduced threshold to get more comps sooner
                print("🏘️ Supplementing with neighborhood-based search...")
                neighborhood_comps = self._get_neighborhood_based_comps(target_property)
                if neighborhood_comps:
                    all_comps.extend(neighborhood_comps)
                    print(f"✅ Added {len(neighborhood_comps)} comps from neighborhood search")
            
            if all_comps:
                # Remove duplicates based on address
                seen_addresses = set()
                unique_comps = []
                for comp in all_comps:
                    address_key = comp.get('address', '').lower().strip()
                    if address_key and address_key not in seen_addresses:
                        seen_addresses.add(address_key)
                        unique_comps.append(comp)
                
                # Sort by similarity score (highest first)
                unique_comps.sort(key=lambda x: x.get('similarity_score', 0), reverse=True)
                
                # Limit to top 15 results
                final_comps = unique_comps[:15]
                
                print(f"✅ Returning {len(final_comps)} unique, scored rental comps")
                for i, comp in enumerate(final_comps[:5]):  # Log top 5 for debugging
                    score = comp.get('similarity_score', 0)
                    bed_bath = f"{comp.get('bedrooms', '?')}bd/{comp.get('bathrooms', '?')}ba"
                    price = comp.get('price', 0)
                    print(f"  {i+1}. Score: {score:.1f} | {bed_bath} | ${price:,} | {comp.get('address', 'No address')[:50]}")
                
                return final_comps
            else:
                print("⚠️ No rental comps found with any method")
                return []
                
        except Exception as e:
            print(f"❌ Error getting enhanced property comps: {str(e)}")
            import traceback
            traceback.print_exc()
            return []
    
    def _get_neighborhood_based_comps(self, target_property):
        """Get comps using the original neighborhood-based approach with enhancements"""
        try:
            city = target_property.get('city')
            state = target_property.get('state')
            zipcode = target_property.get('zipcode')
            latitude = target_property.get('latitude')
            longitude = target_property.get('longitude')
            bedrooms = target_property.get('bedrooms')
            
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
            max_neighborhoods_to_check = 8  # Increased from 5 to get more comps
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
                print(f"🔍 Checking neighborhood {i+1}/{max_neighborhoods_to_check}: {hood_name} (ID: {hood_id}){distance_info}")
                
                # Get rental listings for this neighborhood with enhanced filtering
                hood_comps = self._get_traditional_listings_by_neighborhood_enhanced(
                    hood_id, state, target_property, distance
                )
                
                if hood_comps and len(hood_comps) > 0:
                    print(f"✅ Found {len(hood_comps)} filtered comps in {hood_name}")
                    all_comps.extend(hood_comps)
                    
                    # If we have enough comps, stop searching
                    if len(all_comps) >= 15:
                        break
            
            return all_comps
                
        except Exception as e:
            print(f"❌ Error in neighborhood-based comps: {str(e)}")
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
    
    def _get_traditional_listings_by_neighborhood_enhanced(self, neighborhood_id, state, target_property, neighborhood_distance=None):
        """Get traditional rental listings for a specific neighborhood with enhanced filtering"""
        try:
            endpoint = f"{self.base_url}/client/neighborhood/{neighborhood_id}/traditional/listing"
            
            # Create parameters with required fields
            params = {
                "format": "json",
                "state": state
            }
            
            # Add filtering parameters if available
            bedrooms = target_property.get('bedrooms')
            if bedrooms:
                # Try using category parameter for bedroom filtering
                params["category"] = bedrooms
            
            print(f"🔍 Fetching enhanced traditional rental listings for neighborhood ID: {neighborhood_id}")
            response = requests.get(endpoint, headers=self.headers, params=params, timeout=30)
            
            print(f"📡 Request URL: {endpoint}")
            print(f"📊 Response status: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                
                # Enhanced debugging for neighborhood listings
                print(f"📊 Neighborhood API Response: status='{data.get('status')}', has_content={bool(data.get('content'))}")
                if data.get("content"):
                    content = data.get("content", {})
                    if isinstance(content, dict):
                        print(f"📊 Content keys: {list(content.keys())}")
                
                if data.get("status") == "success" and data.get("content"):
                    content = data.get("content", {})
                    
                    # Parse listings from response
                    listings = []
                    if isinstance(content, dict):
                        # Try multiple possible keys where listings might be stored
                        for key in ["results", "properties", "listings", "items", "data"]:
                            if key in content:
                                listings = content[key]
                                print(f"✅ Found listings under '{key}' key: {len(listings)}")
                                break
                        
                        # If no listings found in standard keys, show what's available
                        if not listings and content:
                            print(f"⚠️ No listings found in standard keys. Available keys: {list(content.keys())}")
                            
                    elif isinstance(content, list):
                        listings = content
                        print(f"✅ Content is direct list with {len(listings)} items")
                    
                    print(f"📊 Processing {len(listings)} raw listings from API")
                    
                    # Format and filter the rental comps
                    formatted_comps = []
                    for listing in listings:
                        comp = {
                            "address": listing.get("address", ""),
                            "city": listing.get("city", ""),
                            "state": listing.get("state", ""),
                            "zipcode": listing.get("zipcode", ""),
                            "price": listing.get("price", 0),
                            "rent": listing.get("price", 0),
                            "bedrooms": listing.get("beds", listing.get("bedrooms", 0)),
                            "bathrooms": listing.get("baths", listing.get("bathrooms", 0)),
                            "sqft": listing.get("sqft", 0),
                            "year_built": listing.get("year_built"),
                            "property_type": listing.get("type", ""),
                            "neighborhood": listing.get("neighborhood", ""),
                            "source": "Mashvisor Neighborhood API"
                        }
                        
                        # Add neighborhood distance if available
                        if neighborhood_distance is not None:
                            comp["neighborhood_distance_miles"] = round(neighborhood_distance, 2)
                        
                        # Apply enhanced filtering
                        if self._should_include_comp(comp, target_property):
                            # Calculate similarity score
                            comp['similarity_score'] = self._calculate_similarity_score(comp, target_property)
                            formatted_comps.append(comp)
                    
                    # Sort by similarity score (highest first)
                    formatted_comps.sort(key=lambda x: x.get('similarity_score', 0), reverse=True)
                    
                    print(f"✅ Returning {len(formatted_comps)} filtered and scored comps from neighborhood")
                    return formatted_comps[:10]  # Return top 10 from this neighborhood
                else:
                    print(f"⚠️ No rental listings found in response")
                    return []
            else:
                print(f"⚠️ API returned status code: {response.status_code}")
                return []
                
        except Exception as e:
            print(f"❌ Exception fetching enhanced rental listings: {str(e)}")
            return []
    
    def _should_include_comp(self, comp, target_property):
        """Determine if a comp should be included based on filtering criteria"""
        # Basic validity checks
        if not comp.get('address') or comp.get('price', 0) <= 0:
            return False
        
        # Bedroom filtering (allow ±1 bedroom flexibility)
        target_bedrooms = target_property.get('bedrooms')
        comp_bedrooms = comp.get('bedrooms')
        if target_bedrooms and comp_bedrooms:
            if abs(comp_bedrooms - target_bedrooms) > 1:
                return False
        
        # Bathroom filtering (allow ±1 bathroom flexibility)
        target_bathrooms = target_property.get('bathrooms')
        comp_bathrooms = comp.get('bathrooms')
        if target_bathrooms and comp_bathrooms:
            if abs(comp_bathrooms - target_bathrooms) > 1:
                return False
        
        # Price filtering (keep comps within 50% to 200% of target price)
        target_price = target_property.get('price')
        comp_price = comp.get('price')
        if target_price and comp_price and target_price > 0 and comp_price > 0:
            price_ratio = comp_price / target_price
            if price_ratio < 0.5 or price_ratio > 2.0:
                return False
        
        return True

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