import React, { useState, useEffect } from 'react';
import { checkApiStatus, searchProperties } from './services/api';
import SearchForm from './components/SearchForm';
import PropertyList from './components/PropertyList';
import { MortgageProvider } from './context/MortgageContext';
import 'bootstrap/dist/css/bootstrap.min.css';
import './index.css';

function App() {
  const [properties, setProperties] = useState([]);
  const [loading, setLoading] = useState(false);
  const [apiConnected, setApiConnected] = useState(false);
  const [apiError, setApiError] = useState(null);

  // Check API connection on component mount
  useEffect(() => {
    const checkConnection = async () => {
      try {
        const status = await checkApiStatus();
        setApiConnected(status.connected);
        if (!status.connected) {
          setApiError(status.error);
        }
      } catch (error) {
        setApiConnected(false);
        setApiError(error.message);
      }
    };
    
    checkConnection();
  }, []);

  // Handle search using our API service
  const handleSearch = async (searchParams) => {
    try {
      setLoading(true);
      const results = await searchProperties(searchParams);
      setProperties(results);
    } catch (error) {
      console.error("Search error:", error);
      alert("Error searching properties. Please try again.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <MortgageProvider>
      {/* Application container */}
      <div className="container py-4">
        <header className="text-center mb-5">
          <h1>DSCR Property Analyzer</h1>
          <p className="lead">Find investment properties with the best debt service coverage ratio</p>
        </header>

        {/* API Status Indicator */}
        <div className="api-status mb-4">
          {apiConnected ? (
            <div className="alert alert-success">✅ API Connected</div>
          ) : (
            <div className="alert alert-danger">
              ❌ API Disconnected
              {apiError && <div className="mt-2">Error: {apiError}</div>}
            </div>
          )}
        </div>

        {/* Debug info */}
        {properties.length > 0 && (
          <div className="alert alert-info">
            Found {properties.length} properties in state
          </div>
        )}

        {/* Search Form */}
        <div className="row">
          <div className="col-md-4">
            <SearchForm 
              onSearch={handleSearch} 
              loading={loading} 
              apiConnected={apiConnected} 
            />
          </div>
          
          <div className="col-md-8">
            {properties.length > 0 ? (
              <PropertyList properties={properties} />
            ) : (
              <div className="text-center mt-5 p-5 bg-light rounded">
                {loading ? (
                  <p>Searching for properties...</p>
                ) : (
                  <p>Use the search form to find investment properties</p>
                )}
              </div>
            )}
          </div>
        </div>
      </div>
    </MortgageProvider>
  );
}

export default App;
