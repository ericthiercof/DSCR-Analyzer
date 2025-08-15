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
        return []  # Return empty list on error