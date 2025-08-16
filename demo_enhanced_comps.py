#!/usr/bin/env python3
"""
Demo showing how enhanced comps functionality will work with real data.
This simulates API responses to demonstrate the full workflow.
"""

import sys
import os

# Set test API key before importing
os.environ['MASHVISOR_API_KEY'] = 'demo_key_for_testing'

sys.path.append('/home/runner/work/DSCR-Analyzer/DSCR-Analyzer')

from backend.mashvisor_search import MashvisorPropertySearch

def demo_with_mock_data():
    """Demonstrate the enhanced workflow with mock API responses"""
    print("🎭 Demo: Enhanced Comps Functionality with Mock Data")
    print("=" * 60)
    
    search = MashvisorPropertySearch()
    
    # Simulate two different properties
    properties = [
        {
            "name": "Houston Luxury Property",
            "city": "Houston",
            "state": "TX",
            "zipcode": "77001",
            "bedrooms": 4,
            "bathrooms": 3,
            "price": 450000,
            "latitude": 29.7604,
            "longitude": -95.3698
        },
        {
            "name": "Austin Starter Home",
            "city": "Austin", 
            "state": "TX",
            "zipcode": "73301",
            "bedrooms": 2,
            "bathrooms": 1,
            "price": 180000,
            "latitude": 30.2672,
            "longitude": -97.7431
        }
    ]
    
    # Mock comp data that would come from the API
    mock_comps_data = {
        "Houston": [
            {"address": "123 Memorial Dr", "bedrooms": 4, "bathrooms": 3, "price": 425000, "sqft": 2100, "neighborhood_distance_miles": 0.8},
            {"address": "456 Westheimer Rd", "bedrooms": 4, "bathrooms": 2.5, "price": 475000, "sqft": 2300, "neighborhood_distance_miles": 1.2},
            {"address": "789 Richmond Ave", "bedrooms": 3, "bathrooms": 2, "price": 380000, "sqft": 1800, "neighborhood_distance_miles": 2.1},
            {"address": "321 Main St", "bedrooms": 5, "bathrooms": 4, "price": 520000, "sqft": 2800, "neighborhood_distance_miles": 1.5},
            {"address": "654 Louisiana St", "bedrooms": 3, "bathrooms": 3, "price": 410000, "sqft": 1950, "neighborhood_distance_miles": 0.6}
        ],
        "Austin": [
            {"address": "111 South Congress", "bedrooms": 2, "bathrooms": 1, "price": 175000, "sqft": 900, "neighborhood_distance_miles": 0.5},
            {"address": "222 East 6th St", "bedrooms": 2, "bathrooms": 1.5, "price": 195000, "sqft": 1000, "neighborhood_distance_miles": 1.1},
            {"address": "333 Lamar Blvd", "bedrooms": 1, "bathrooms": 1, "price": 145000, "sqft": 750, "neighborhood_distance_miles": 1.8},
            {"address": "444 Guadalupe St", "bedrooms": 3, "bathrooms": 2, "price": 215000, "sqft": 1200, "neighborhood_distance_miles": 2.2},
            {"address": "555 Barton Springs", "bedrooms": 2, "bathrooms": 2, "price": 210000, "sqft": 1100, "neighborhood_distance_miles": 0.9}
        ]
    }
    
    for property_data in properties:
        print(f"\n🏠 Processing: {property_data['name']}")
        print(f"   📍 {property_data['city']}, {property_data['state']} {property_data['zipcode']}")
        print(f"   🏘️ {property_data['bedrooms']}bd/{property_data['bathrooms']}ba, ${property_data['price']:,}")
        
        # Get mock comps for this city
        city_comps = mock_comps_data.get(property_data['city'], [])
        
        # Process comps through our enhanced filtering and scoring
        scored_comps = []
        for comp in city_comps:
            # Add source for realism
            comp['source'] = 'Mashvisor Long-term Comps API'
            
            # Check if comp should be included
            if search._should_include_comp(comp, property_data):
                # Calculate similarity score
                comp['similarity_score'] = search._calculate_similarity_score(comp, property_data)
                scored_comps.append(comp)
        
        # Sort by similarity score
        scored_comps.sort(key=lambda x: x['similarity_score'], reverse=True)
        
        print(f"\n   📊 Found {len(scored_comps)} relevant comps (from {len(city_comps)} total):")
        print("   " + "-" * 70)
        
        for i, comp in enumerate(scored_comps[:5], 1):  # Show top 5
            score = comp['similarity_score']
            bed_bath = f"{comp['bedrooms']}bd/{comp['bathrooms']}ba"
            price = f"${comp['price']:,}"
            distance = f"{comp['neighborhood_distance_miles']} mi"
            
            # Color code the score
            if score >= 90:
                score_color = "🟢"
            elif score >= 70:
                score_color = "🟡"  
            else:
                score_color = "🔴"
            
            print(f"   {i}. {score_color} {score:5.1f}% | {bed_bath:>8} | {price:>10} | {distance:>6} | {comp['address']}")
        
        if len(scored_comps) == 0:
            print("   ⚠️  No qualifying comps found (all filtered out)")
    
    print(f"\n🎯 Key Improvements Demonstrated:")
    print("   ✅ Different properties get different, relevant comps")
    print("   ✅ Comps are ranked by similarity to target property")
    print("   ✅ Properties outside range are filtered out")
    print("   ✅ Visual scoring helps identify best matches")
    print("   ✅ Distance and property features influence ranking")

def show_filtering_differences():
    """Show how filtering creates different results for different properties"""
    print(f"\n\n🔍 Filtering Comparison: Same City, Different Properties")
    print("=" * 60)
    
    search = MashvisorPropertySearch()
    
    # Same mock comp pool for both properties
    shared_comps = [
        {"address": "100 Main St", "bedrooms": 2, "bathrooms": 1, "price": 150000, "sqft": 800},
        {"address": "200 Oak Ave", "bedrooms": 3, "bathrooms": 2, "price": 200000, "sqft": 1200},
        {"address": "300 Pine St", "bedrooms": 4, "bathrooms": 3, "price": 350000, "sqft": 2000},
        {"address": "400 Elm Dr", "bedrooms": 1, "bathrooms": 1, "price": 120000, "sqft": 600},
        {"address": "500 Cedar Ln", "bedrooms": 5, "bathrooms": 4, "price": 500000, "sqft": 3000}
    ]
    
    # Two different target properties
    targets = [
        {"name": "Budget Starter", "bedrooms": 2, "bathrooms": 1, "price": 160000},
        {"name": "Family Home", "bedrooms": 4, "bathrooms": 3, "price": 320000}
    ]
    
    for target in targets:
        print(f"\n🎯 Target: {target['name']} ({target['bedrooms']}bd/{target['bathrooms']}ba, ${target['price']:,})")
        
        qualifying_comps = []
        for comp in shared_comps:
            if search._should_include_comp(comp, target):
                comp['similarity_score'] = search._calculate_similarity_score(comp, target)
                qualifying_comps.append(comp)
        
        qualifying_comps.sort(key=lambda x: x['similarity_score'], reverse=True)
        
        print(f"   Qualifying comps: {len(qualifying_comps)}/5")
        for comp in qualifying_comps:
            score = comp['similarity_score']
            bed_bath = f"{comp['bedrooms']}bd/{comp['bathrooms']}ba"
            price = f"${comp['price']:,}"
            print(f"   • {score:5.1f}% | {bed_bath:>8} | {price:>10} | {comp['address']}")
        
        if len(qualifying_comps) == 0:
            print("   • No qualifying comps (all filtered out)")
    
    print(f"\n💡 Result: Same data pool produces different, targeted results for each property!")

if __name__ == "__main__":
    try:
        demo_with_mock_data()
        show_filtering_differences()
        
        print(f"\n\n🎉 Demo Complete!")
        print("This shows how the enhanced comps system will work with real API data:")
        print("• Property-specific filtering eliminates poor matches")
        print("• Similarity scoring ranks remaining comps by relevance") 
        print("• Different properties get appropriately different results")
        print("• Visual indicators help users identify best matches")
        
    except Exception as e:
        print(f"❌ Demo failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)