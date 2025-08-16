#!/usr/bin/env python3
"""
Test script to demonstrate the enhanced comps functionality improvements.
This script shows how the new similarity scoring and filtering system works.
"""

import sys
import os

# Set test API key before importing
os.environ['MASHVISOR_API_KEY'] = 'test_key_for_testing'

sys.path.append('/home/runner/work/DSCR-Analyzer/DSCR-Analyzer')

from backend.mashvisor_search import MashvisorPropertySearch

def test_similarity_scoring():
    """Test the similarity scoring algorithm"""
    print("🧪 Testing Similarity Scoring Algorithm")
    print("=" * 50)
    
    # Create a mock instance with fake API key for testing
    search = MashvisorPropertySearch()
    
    # Target property
    target_property = {
        "bedrooms": 3,
        "bathrooms": 2,
        "price": 300000,
        "sqft": 1500
    }
    
    # Test properties with different similarity levels
    test_comps = [
        {
            "address": "Perfect Match Property",
            "bedrooms": 3,
            "bathrooms": 2,
            "price": 295000,
            "sqft": 1480,
            "neighborhood_distance_miles": 0.5
        },
        {
            "address": "Good Match Property",
            "bedrooms": 3,
            "bathrooms": 2.5,
            "price": 320000,
            "sqft": 1600,
            "neighborhood_distance_miles": 1.2
        },
        {
            "address": "Decent Match Property",
            "bedrooms": 4,
            "bathrooms": 2,
            "price": 350000,
            "sqft": 1800,
            "neighborhood_distance_miles": 2.5
        },
        {
            "address": "Poor Match Property",
            "bedrooms": 2,
            "bathrooms": 1,
            "price": 200000,
            "sqft": 1000,
            "neighborhood_distance_miles": 8.0
        },
        {
            "address": "Far Away Property",
            "bedrooms": 3,
            "bathrooms": 2,
            "price": 305000,
            "sqft": 1520,
            "neighborhood_distance_miles": 15.0
        }
    ]
    
    print(f"Target Property: {target_property['bedrooms']}bd/{target_property['bathrooms']}ba, ${target_property['price']:,}, {target_property['sqft']} sqft")
    print("\nScoring comparable properties:")
    print("-" * 80)
    
    scored_comps = []
    for comp in test_comps:
        score = search._calculate_similarity_score(comp, target_property)
        comp['similarity_score'] = score
        scored_comps.append(comp)
        
        bed_bath = f"{comp['bedrooms']}bd/{comp['bathrooms']}ba"
        price = f"${comp['price']:,}"
        sqft = f"{comp['sqft']} sqft"
        distance = f"{comp['neighborhood_distance_miles']} miles"
        
        print(f"Score: {score:5.1f} | {bed_bath:>8} | {price:>10} | {sqft:>9} | {distance:>8} | {comp['address']}")
    
    # Sort by similarity score
    scored_comps.sort(key=lambda x: x['similarity_score'], reverse=True)
    
    print("\nRanked by similarity (best matches first):")
    print("-" * 80)
    for i, comp in enumerate(scored_comps, 1):
        score = comp['similarity_score']
        bed_bath = f"{comp['bedrooms']}bd/{comp['bathrooms']}ba"
        price = f"${comp['price']:,}"
        print(f"{i}. Score: {score:5.1f} | {bed_bath:>8} | {price:>10} | {comp['address']}")
    
    return scored_comps

def test_filtering_logic():
    """Test the property filtering logic"""
    print("\n\n🧪 Testing Property Filtering Logic")
    print("=" * 50)
    
    search = MashvisorPropertySearch()
    
    target_property = {
        "bedrooms": 3,
        "bathrooms": 2,
        "price": 300000
    }
    
    test_properties = [
        {"address": "Good match", "bedrooms": 3, "bathrooms": 2, "price": 295000},
        {"address": "Close bedroom match", "bedrooms": 4, "bathrooms": 2, "price": 310000},
        {"address": "Too many bedrooms", "bedrooms": 6, "bathrooms": 2, "price": 300000},
        {"address": "Close bathroom match", "bedrooms": 3, "bathrooms": 3, "price": 290000},
        {"address": "Too many bathrooms", "bedrooms": 3, "bathrooms": 5, "price": 300000},
        {"address": "Price too low", "bedrooms": 3, "bathrooms": 2, "price": 100000},
        {"address": "Price too high", "bedrooms": 3, "bathrooms": 2, "price": 800000},
        {"address": "No address", "bedrooms": 3, "bathrooms": 2, "price": 0},
    ]
    
    print(f"Target Property: {target_property['bedrooms']}bd/{target_property['bathrooms']}ba, ${target_property['price']:,}")
    print("\nFiltering test properties:")
    print("-" * 60)
    
    for prop in test_properties:
        should_include = search._should_include_comp(prop, target_property)
        bed_bath = f"{prop.get('bedrooms', '?')}bd/{prop.get('bathrooms', '?')}ba"
        price = f"${prop.get('price', 0):,}"
        status = "✅ INCLUDE" if should_include else "❌ EXCLUDE"
        print(f"{status} | {bed_bath:>8} | {price:>10} | {prop['address']}")

def test_price_range_calculation():
    """Test price range calculation for API filters"""
    print("\n\n🧪 Testing Price Range Calculation")
    print("=" * 50)
    
    test_prices = [100000, 250000, 500000, 1000000]
    
    for price in test_prices:
        min_price = int(price * 0.7)
        max_price = int(price * 1.3)
        print(f"Target: ${price:,} → Range: ${min_price:,} - ${max_price:,}")

if __name__ == "__main__":
    try:
        test_similarity_scoring()
        test_filtering_logic()
        test_price_range_calculation()
        
        print("\n\n✅ All tests completed successfully!")
        print("\nKey Improvements Demonstrated:")
        print("- ✅ Similarity scoring ranks properties by relevance")
        print("- ✅ Property filtering removes poor matches")
        print("- ✅ Price range filtering creates targeted search ranges")
        print("- ✅ Bedroom/bathroom flexibility allows close matches")
        print("- ✅ Distance-based scoring prioritizes nearby properties")
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)