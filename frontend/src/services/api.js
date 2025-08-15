import axios from 'axios';

// Create an axios instance with configuration
const api = axios.create({
  baseURL: 'http://127.0.0.1:8000',
  timeout: 10000,
  headers: {
    'Content-Type': 'application/json'
  }
});

// Check API status
export const checkApiStatus = async () => {
  try {
    const response = await api.get('/');
    return { connected: true, message: response.data.message };
  } catch (error) {
    console.error('API connection error:', error);
    return { connected: false, error: error.message };
  }
};

// Search properties
export const searchProperties = async (searchParams) => {
  try {
    console.log('API service: Sending search request with params:', searchParams);
    
    const response = await api.post('/api/search', searchParams);
    console.log('API Response:', response.data);
    
    // Check for the expected property structure
    if (response.data && Array.isArray(response.data.properties)) {
      console.log(`Found ${response.data.properties.length} properties`);
      return response.data.properties;
    } else if (response.data && Array.isArray(response.data)) {
      console.log(`Found ${response.data.length} properties (direct array)`);
      return response.data;
    } else {
      console.error('Unexpected response format:', response.data);
      return [];
    }
  } catch (error) {
    console.error('Error searching properties:', error);
    
    // Enhanced error logging
    if (error.response) {
      console.error('Response status:', error.response.status);
      console.error('Response data:', error.response.data);
    }
    
    throw error;
  }
};

// Get property comps - simplified to just extract state from address
export const getPropertyComps = async (propertyData) => {
  try {
    // Extract location data from address
    let state = 'TX'; // Default fallback
    let city = '';
    let zip = '';
    
    if (propertyData.address) {
      // Extract zip code (5 digits at the end)
      const zipMatch = propertyData.address.match(/(\d{5})(?!.*\d{5})/);
      if (zipMatch) zip = zipMatch[1];
      
      // Extract state (2 capital letters before zip)
      const stateMatch = propertyData.address.match(/,\s+([A-Z]{2})\s+\d{5}/);
      if (stateMatch) state = stateMatch[1];
      
      // Extract city (between commas before state)
      const cityMatch = propertyData.address.match(/,\s+([^,]+),\s+[A-Z]{2}/);
      if (cityMatch) city = cityMatch[1].trim();
    }
    
    // Create data to send to API with enhanced location info
    const requestData = {
      zpid: propertyData.zpid,
      address: propertyData.address,
      bedrooms: propertyData.bedrooms,
      bathrooms: propertyData.bathrooms,
      price: propertyData.price,
      state: state,
      city: city,
      zip: zip,
      // Add coordinates if available
      latitude: propertyData.latitude || propertyData.lat,
      longitude: propertyData.longitude || propertyData.lng
    };
    
    console.log('Fetching comps for property:', requestData);
    console.log('Coordinates being sent:', {
      lat: propertyData.latitude || propertyData.lat, 
      lng: propertyData.longitude || propertyData.lng
    });
    const response = await api.post('/api/property-comps', requestData);
    
    if (response.data && Array.isArray(response.data)) {
      return response.data;
    } else {
      console.error('Unexpected comps response format:', response.data);
      return [];
    }
  } catch (error) {
    console.error('Error fetching property comps:', error);
    throw error;
  }
};

// Get detailed property analysis from Mashvisor
export const getPropertyAnalysis = async (propertyData) => {
  try {
    const response = await api.post('/api/property-analysis', propertyData);
    return response.data;
  } catch (error) {
    console.error('Error getting property analysis:', error);
    throw error;
  }
};

export default api;