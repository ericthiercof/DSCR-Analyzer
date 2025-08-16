# Mashvisor API Documentation

This document contains the complete API documentation from Mashvisor (https://www.mashvisor.com/api-doc/) for reference in the DSCR Investment Property Analyzer project.

## Base API Endpoint
```
https://api.mashvisor.com/v1.1/client
```

## Authentication
All requests require the `x-api-key` header with your Mashvisor API key.

## Long Term Rentals

### Get Long Term Rental Comps
Get rental comps for a specific city and state.

**Endpoint:** `GET /client/long-term-comps`

**Parameters:**
- `state` (required) - State abbreviation (e.g., "GA")
- `city` (required) - City name (e.g., "Dahlonega")
- `min_price` (optional) - Minimum price filter
- `max_price` (optional) - Maximum price filter

**Example Request:**
```
GET https://api.mashvisor.com/v1.1/client/long-term-comps?state=GA&city=Dahlonega
```

### Get Traditional Comparable Listings
Get traditional rental listings for a specific neighborhood.

**Endpoint:** `GET /client/neighborhood/{neighborhood_id}/traditional/listing`

**Parameters:**
- `neighborhood_id` (required) - Neighborhood ID
- `state` (required) - State abbreviation
- `format` (optional) - Response format (json, xml) - default: json
- `items` (optional) - Number of items per page
- `page` (optional) - Page number
- `sort_by` (optional) - Sort field (address, price, etc.)
- `order` (optional) - Sort order (asc, desc)
- `pid` (optional) - Property ID for context

**Example Request:**
```
GET https://api.mashvisor.com/v1.1/client/neighborhood/397651/traditional/listing?format=json&items=9&order=desc&page=1&state=ny
```

## City and Neighborhood Data

### Get City Neighborhoods
Get all neighborhoods for a specific city.

**Endpoint:** `GET /client/city/neighborhoods/{state}/{city}`

**Parameters:**
- `state` (required) - State abbreviation
- `city` (required) - City name (URL encoded)

**Example Request:**
```
GET https://api.mashvisor.com/v1.1/client/city/neighborhoods/FL/Miami
```

**Response Structure:**
```json
{
  "status": "success",
  "content": {
    "results": [
      {
        "id": 123456,
        "name": "Downtown",
        "latitude": 25.7617,
        "longitude": -80.1918
      }
    ]
  }
}
```

### Get City Investment Overview
Get investment metrics for a city.

**Endpoint:** `GET /client/city/investment/{state}/{city}`

**Response includes:**
- `median_price` - Median property price
- `traditional_properties` - Number of traditional rental properties
- `airbnb_properties` - Number of Airbnb properties
- `traditional_rental` - Average traditional rental income
- `traditional_rental_rates` - Rental rates by bedroom count
- `traditional_coc` - Traditional cash-on-cash return

## Property Data

### Get Traditional Property
Get detailed information about a specific traditional rental property.

**Endpoint:** `GET /client/traditional/{property_id}`

### Get Property Investment Breakdown
Get investment analysis for a specific property.

**Endpoint:** `GET /client/property/investment/{property_id}`

## Response Format

All successful responses follow this structure:
```json
{
  "status": "success",
  "content": {
    // API-specific data
  },
  "message": "Success message"
}
```

Error responses:
```json
{
  "status": "error",
  "message": "Error description"
}
```

## Rate Limits
- Standard API limits apply
- Use appropriate delays between requests to avoid rate limiting

## Best Practices for Comps

1. **Use Neighborhood-Based Filtering**: Start with neighborhoods closest to the target property
2. **Apply Property Filters**: Filter by bedrooms, bathrooms, and price range for better similarity
3. **Sort by Relevance**: Sort results by distance and property characteristic similarity
4. **Limit Results**: Request reasonable number of comps to avoid API overload
5. **Cache Results**: Cache neighborhood data to reduce API calls

## Property Similarity Scoring

To improve comp relevance, consider scoring based on:
- Distance from target property (weight: 30%)
- Bedroom count match (weight: 25%)
- Bathroom count match (weight: 20%)
- Price proximity (weight: 15%)
- Square footage similarity (weight: 10%)

## Implementation Notes

- URL encode city names with spaces
- Handle API timeouts gracefully
- Implement exponential backoff for retries
- Log API responses for debugging
- Use coordinates when available for better proximity calculations