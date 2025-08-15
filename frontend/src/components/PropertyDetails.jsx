import React, { useState } from 'react';

const PropertyDetails = ({ property }) => {
  const [rentalComps, setRentalComps] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const handleLongTermCompsClick = async () => {
    setLoading(true);
    setError(null);
    
    try {
      // Prepare property data with the necessary fields
      const propertyData = {
        address: property.address,
        city: property.address.split(',')[0].trim(), // Extract city from address
        state: property.address.split(',')[1]?.trim(), // Extract state from address
        zipcode: property.address.split(' ').pop(), // Extract zipcode from address
        bedrooms: property.bedrooms,
        bathrooms: property.bathrooms,
        price: property.price
      };

      // Call the API endpoint
      const response = await fetch('/api/property-comps', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(propertyData),
      });
      
      const data = await response.json();
      
      if (data.success) {
        setRentalComps(data.comps);
      } else {
        setError(data.detail || 'Error fetching rental comps');
      }
    } catch (error) {
      console.error("Error fetching rental comps:", error);
      setError("Failed to fetch rental comps. Please try again.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="property-details">
      <h2>{property.address}</h2>
      
      <div className="property-info">
        <p><strong>Price:</strong> ${property.price.toLocaleString()}</p>
        <p><strong>Bedrooms:</strong> {property.bedrooms}</p>
        <p><strong>Bathrooms:</strong> {property.bathrooms}</p>
        <p><strong>Monthly Payment:</strong> ${property.monthly_payment.toLocaleString()}</p>
        <p><strong>DSCR:</strong> {property.dscr}</p>
      </div>
      
      <div className="property-actions">
        <button 
          onClick={handleLongTermCompsClick}
          disabled={loading}
          className="btn btn-primary"
        >
          {loading ? 'Loading Comps...' : 'Get Long Term Comps'}
        </button>
        {error && <p className="text-danger">{error}</p>}
      </div>
      
      {rentalComps.length > 0 && (
        <div className="rental-comps">
          <h3>Rental Comps</h3>
          <table className="table">
            <thead>
              <tr>
                <th>Address</th>
                <th>Beds</th>
                <th>Baths</th>
                <th>Rent</th>
              </tr>
            </thead>
            <tbody>
              {rentalComps.map((comp, index) => (
                <tr key={index}>
                  <td>{comp.address}</td>
                  <td>{comp.bedrooms}</td>
                  <td>{comp.bathrooms}</td>
                  <td>${comp.rent}</td>
                </tr>
              ))}
            </tbody>
          </table>
          
          <div className="comp-summary">
            <p><strong>Average Rent:</strong> $
              {(rentalComps.reduce((sum, comp) => sum + comp.rent, 0) / rentalComps.length).toFixed(2)}
            </p>
          </div>
        </div>
      )}
    </div>
  );
};

export default PropertyDetails;