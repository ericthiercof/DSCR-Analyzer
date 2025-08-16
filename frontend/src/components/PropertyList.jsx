// filepath: /workspaces/blank-app/frontend/src/components/PropertyList.jsx
import React, { useState } from 'react';
import { getPropertyComps, getPropertyAnalysis } from '../services/api';
import { useMortgage } from '../context/MortgageContext';

// Helper function to determine DSCR grade
const getDscrGrade = (dscr) => {
  if (!dscr) return { grade: 'N/A', color: 'secondary' };
  
  if (dscr >= 2.0) return { grade: 'A+', color: 'success' };
  if (dscr >= 1.8) return { grade: 'A', color: 'success' };
  if (dscr >= 1.6) return { grade: 'A-', color: 'success' };
  if (dscr >= 1.4) return { grade: 'B+', color: 'primary' };
  if (dscr >= 1.2) return { grade: 'B', color: 'primary' };
  if (dscr >= 1.0) return { grade: 'B-', color: 'primary' };
  if (dscr >= 0.9) return { grade: 'C+', color: 'warning' };
  if (dscr >= 0.8) return { grade: 'C', color: 'warning' };
  if (dscr >= 0.7) return { grade: 'C-', color: 'warning' };
  if (dscr >= 0.6) return { grade: 'D+', color: 'danger' };
  if (dscr >= 0.5) return { grade: 'D', color: 'danger' };
  return { grade: 'D-', color: 'danger' };
};

// Helper function to calculate monthly payment breakdown
const calculateMonthlyPayment = (price, interestRate, downPaymentPercent, termYears = 30, propertyTax = 0, insurance = 0, hoa = 0) => {
  // Calculate loan amount
  const downPayment = price * (downPaymentPercent / 100);
  const loanAmount = price - downPayment;
  
  // Calculate monthly mortgage payment (principal + interest)
  const monthlyRate = interestRate / 100 / 12;
  const numberOfPayments = termYears * 12;
  const mortgagePayment = loanAmount * (monthlyRate * Math.pow(1 + monthlyRate, numberOfPayments)) / 
                         (Math.pow(1 + monthlyRate, numberOfPayments) - 1);
  
  // Calculate monthly property tax and insurance
  const monthlyPropertyTax = propertyTax / 12;
  const monthlyInsurance = insurance / 12;
  const monthlyHOA = hoa;
  
  // Calculate total payment
  const totalPayment = mortgagePayment + monthlyPropertyTax + monthlyInsurance + monthlyHOA;
  
  return {
    total: totalPayment,
    mortgage: mortgagePayment,
    propertyTax: monthlyPropertyTax,
    insurance: monthlyInsurance,
    hoa: monthlyHOA,
    downPayment: downPayment
  };
};

const PropertyList = ({ properties }) => {
  const [loadingComps, setLoadingComps] = useState({});
  const [comps, setComps] = useState({});
  const [expandedPayments, setExpandedPayments] = useState({});
  const [propertyAnalysis, setPropertyAnalysis] = useState({});
  const [loadingAnalysis, setLoadingAnalysis] = useState(false);
  
  // Get mortgage settings from context instead of hardcoded values
  const { settings } = useMortgage();
  const interestRate = settings.interestRate;
  const downPaymentPercent = settings.downPaymentPercent;

  // Debug first property to see all available fields
  React.useEffect(() => {
    if (properties && properties.length > 0) {
      console.log("First property data:", properties[0]);
      console.log("Rent estimate field check:", {
        rentZestimate: properties[0].rentZestimate,
        rentEstimate: properties[0].rentEstimate,
        rent_estimate: properties[0].rent_estimate,
        estimated_rent: properties[0].estimated_rent,
        monthlyRent: properties[0].monthlyRent,
        monthly_rent: properties[0].monthly_rent,
        rent: properties[0].rent
      });
    }
  }, [properties]);

  // Function to get property comps
  const fetchPropertyComps = async (property) => {
    if (!property.zpid) {
      alert("Property ID not available for comps");
      return;
    }

    // Update loading state
    setLoadingComps(prev => ({ ...prev, [property.zpid]: true }));

    try {
      const propertyComps = await getPropertyComps({
        zpid: property.zpid,
        address: property.address,
        bedrooms: property.bedrooms,
        bathrooms: property.bathrooms,
        price: property.price,
        state: property.state || property.address.split(',').pop().trim().substring(0,2)
      });
      
      setComps(prev => ({
        ...prev,
        [property.zpid]: propertyComps
      }));
    } catch (error) {
      console.error("Error fetching comps:", error);
      alert("Failed to fetch rental comps. Please try again.");
    } finally {
      setLoadingComps(prev => ({ ...prev, [property.zpid]: false }));
    }
  };

  // Function to fetch property analysis
  const fetchPropertyAnalysis = async (property) => {
    if (!property.zpid) {
      alert("Property ID not available for analysis");
      return;
    }

    // Update loading state
    setLoadingAnalysis(true);

    try {
      // Extract the actual city from the address
      const addressParts = property.address.split(',');
      const city = addressParts.length > 1 ? addressParts[1].trim().split(' ')[0] : '';
      
      const analysisData = await getPropertyAnalysis({
        zpid: property.zpid,
        address: property.address,
        bedrooms: property.bedrooms,
        bathrooms: property.bathrooms,
        price: property.price,
        state: property.state || property.address.split(',').pop().trim().substring(0,2),
        city: city
      });
      
      setPropertyAnalysis(prev => ({
        ...prev,
        [property.zpid]: analysisData
      }));
    } catch (error) {
      console.error("Error fetching property analysis:", error);
      
      // Add the error as a property analysis result
      setPropertyAnalysis(prev => ({
        ...prev,
        [property.zpid]: {
          source: "Error",
          message: "Failed to fetch property analysis. The server may be experiencing high load."
        }
      }));
    } finally {
      setLoadingAnalysis(false);
    }
  };

  // Toggle payment details expanded/collapsed
  const togglePaymentDetails = (zpid) => {
    setExpandedPayments(prev => ({
      ...prev,
      [zpid]: !prev[zpid]
    }));
  };

  // Generate Zillow URL from property address
  const getZillowUrl = (property) => {
    if (property.detailUrl) {
      return `https://www.zillow.com${property.detailUrl}`;
    }
    
    if (property.zpid) {
      return `https://www.zillow.com/homedetails/${property.zpid}_zpid/`;
    }
    
    // If no detailUrl or zpid, create a search URL based on address
    const formattedAddress = property.address.replace(/\s+/g, '-').replace(/,/g, '');
    return `https://www.zillow.com/homes/${formattedAddress}_rb/`;
  };

  // Generate Redfin URL from property address
  const getRedfinUrl = (property) => {
    return `https://www.redfin.com/search/real-estate-listings?q=${encodeURIComponent(property.address)}`;
  };

  // Validate properties
  if (!Array.isArray(properties)) {
    console.error('Properties is not an array:', properties);
    return <div className="alert alert-danger">Error: Invalid property data format</div>;
  }
  
  if (properties.length === 0) {
    return (
      <div className="alert alert-info">
        No properties found matching your criteria. Try adjusting your search.
      </div>
    );
  }

  return (
    <div className="property-list">
      <h2>Properties Found: {properties.length}</h2>
      <div className="row">
        {properties.map((property, index) => {
          // Calculate DSCR grade
          const { grade, color } = property.dscr ? 
            getDscrGrade(property.dscr) : 
            { grade: 'N/A', color: 'secondary' };
            
          // Calculate monthly payment
          const propertyTax = property.annual_tax || property.price * 0.01; // Estimate 1% if not provided
          const insurance = property.price * 0.003; // Estimate 0.3% annually for insurance
          const hoa = property.hoa_fee || 0;
          
          const payments = calculateMonthlyPayment(
            property.price, 
            interestRate, 
            downPaymentPercent, 
            30, // 30 year mortgage
            propertyTax, 
            insurance, 
            hoa
          );

          return (
            <div className="col-md-6 mb-4" key={index}>
              <div className="card h-100">
                {property.imgSrc && (
                  <img 
                    src={property.imgSrc} 
                    className="card-img-top" 
                    alt={property.address || "Property"} 
                    style={{height: "200px", objectFit: "cover"}}
                  />
                )}
                <div className="card-body">
                  <div className="d-flex justify-content-between align-items-start mb-2">
                    <h5 className="card-title mb-0">{property.address || "Unknown Address"}</h5>
                    <div className="d-flex flex-column align-items-end">
                      {/* DSCR Badge */}
                      <span className={`badge bg-${color} fs-6 mb-1`}>
                        DSCR: {property.dscr ? property.dscr.toFixed(2) : "N/A"} 
                        <span className="ms-1">({grade})</span>
                      </span>
                      
                      {/* Rent Estimate Badge */}
                      {(property.rentZestimate || property.rentEstimate || property.monthly_rent || 
                        property.estimated_rent || property.rent_estimate || property.monthlyRent || property.rent) && (
                        <span key={`rent-${property.zpid}`} className="badge bg-info fs-6">
                          Rent: ${(property.rentZestimate || property.rentEstimate || property.monthly_rent || 
                                 property.estimated_rent || property.rent_estimate || property.monthlyRent || 
                                 property.rent || 0).toLocaleString()}/mo
                          {(property.rentZestimate || property.rentEstimate) && (
                            <span className="badge bg-warning text-dark ms-1" style={{fontSize: '0.7em'}}>Zillow Estimate</span>
                          )}
                        </span>
                      )}
                    </div>
                  </div>
                  
                  <p className="card-text">
                    <strong>Price:</strong> ${property.price?.toLocaleString() || "N/A"}<br />
                    <strong>Beds/Baths:</strong> {property.bedrooms || "?"}/{property.bathrooms || "?"}
                  </p>

                  {/* Monthly Payment Section with Dropdown */}
                  <div className="card mb-3">
                    <div 
                      className="card-header d-flex justify-content-between align-items-center" 
                      style={{cursor: 'pointer'}}
                      onClick={() => togglePaymentDetails(property.zpid || index)}
                    >
                      <strong>Est. Monthly Payment:</strong> ${payments.total.toFixed(0).toLocaleString()}
                      <i className={`bi bi-chevron-${expandedPayments[property.zpid || index] ? 'up' : 'down'}`}></i>
                    </div>
                    
                    {expandedPayments[property.zpid || index] && (
                      <div className="card-body py-2">
                        <small className="d-block">Principal & Interest: ${payments.mortgage.toFixed(0).toLocaleString()}/mo</small>
                        <small className="d-block">Property Tax: ${payments.propertyTax.toFixed(0).toLocaleString()}/mo</small>
                        <small className="d-block">Insurance: ${payments.insurance.toFixed(0).toLocaleString()}/mo</small>
                        {payments.hoa > 0 && (
                          <small className="d-block">HOA: ${payments.hoa.toFixed(0).toLocaleString()}/mo</small>
                        )}
                        <small className="d-block text-muted mt-1">
                          {downPaymentPercent}% down (${payments.downPayment.toFixed(0).toLocaleString()}) at {interestRate}% interest
                        </small>
                      </div>
                    )}
                  </div>
                  
                  {property.monthly_rent && (
                    <p className="card-text">
                      <strong>Monthly Rent:</strong> ${property.monthly_rent.toLocaleString()}<br />
                      <strong>Monthly Mortgage:</strong> ${property.monthly_mortgage?.toLocaleString() || "N/A"}
                    </p>
                  )}
                  
                  {property.cash_flow && (
                    <p className="card-text">
                      <strong>Cash Flow:</strong> 
                      <span className={property.cash_flow >= 0 ? 'text-success' : 'text-danger'}>
                        ${property.cash_flow.toLocaleString()}/mo
                      </span>
                    </p>
                  )}

                  <div className="d-flex flex-column mt-3">
                    <div className="d-flex justify-content-between mb-2">
                      {/* Zillow Link Button */}
                      <a 
                        href={getZillowUrl(property)} 
                        className="btn btn-outline-primary"
                        target="_blank" 
                        rel="noopener noreferrer"
                      >
                        View on Zillow
                      </a>

                      {/* Redfin Link Button - replacing Trulia */}
                      <a 
                        href={getRedfinUrl(property)} 
                        className="btn btn-outline-info"
                        target="_blank" 
                        rel="noopener noreferrer"
                      >
                        View on Redfin
                      </a>
                    </div>

                    <div className="d-flex justify-content-between mb-2">
                      {/* Long-Term Rental Comps Button */}
                      <button
                        className={`btn btn-outline-secondary ${loadingComps[property.zpid] ? 'disabled' : ''}`}
                        onClick={() => fetchPropertyComps(property)}
                        disabled={loadingComps[property.zpid]}
                      >
                        {loadingComps[property.zpid] ? 'Loading...' : 'Long-Term Rental Comps'}
                      </button>

                      {/* Short-Term Rental Comps Button */}
                      <button
                        className="btn btn-outline-dark"
                        onClick={() => alert("Short-term rental comps feature coming soon!")}
                      >
                        Short-Term Rental Comps
                      </button>
                    </div>

                    {/* New Property Analysis Button */}
                    <button
                      className={`btn btn-outline-success ${loadingAnalysis ? 'disabled' : ''}`}
                      onClick={() => fetchPropertyAnalysis(property)}
                      disabled={loadingAnalysis}
                    >
                      {loadingAnalysis ? 'Loading...' : 'Property Analysis'}
                    </button>
                  </div>

                  {/* Comps Display Section */}
                  {comps[property.zpid] !== undefined && (
                    <div className="mt-3 border-top pt-3">
                      <h6>Comparable Rentals {comps[property.zpid].length > 0 && `(${comps[property.zpid].length})`}</h6>
                      {comps[property.zpid].length > 0 ? (
                        <ul className="list-group list-group-flush">
                          {comps[property.zpid].map((comp, idx) => (
                            <li key={idx} className="list-group-item p-2 d-flex justify-content-between">
                              <small>
                                {comp.address || 'Address unavailable'} 
                                {comp.bedrooms && comp.bathrooms && ` - ${comp.bedrooms}bd/${comp.bathrooms}ba`}
                              </small>
                              <span className="badge bg-success">
                                ${comp.price?.toLocaleString() || 0}/mo
                              </span>
                            </li>
                          ))}
                        </ul>
                      ) : (
                        <div className="alert alert-warning">
                          <h6 className="mb-2">No rental comps found</h6>
                          <p className="small mb-1">This could be due to:</p>
                          <ul className="small mb-2">
                            <li>Limited rental data in this area</li>
                            <li>Unique property characteristics</li>
                            <li>API limitations</li>
                          </ul>
                          <p className="small mb-0">
                            <strong>Note:</strong> We do not estimate rental comps. Only actual comparable properties are shown.
                          </p>
                        </div>
                      )}
                    </div>
                  )}

                  {/* Property Analysis Display */}
                  {propertyAnalysis[property.zpid] && (
                    <div className="mt-3 border-top pt-3">
                      <h6>Property Analysis</h6>
                      
                      {propertyAnalysis[property.zpid].source === "NoData" ? (
                        <div className="alert alert-info">
                          <h6 className="mb-2">No Property Data Available</h6>
                          <p className="small mb-0">
                            {propertyAnalysis[property.zpid].message || 
                              "Unable to find specific data for this property. Try searching for comparable properties in the area."}
                          </p>
                        </div>
                      ) : propertyAnalysis[property.zpid].source === "Error" ? (
                        <div className="alert alert-danger">
                          <h6 className="mb-2">Error Retrieving Data</h6>
                          <p className="small mb-0">
                            {propertyAnalysis[property.zpid].message || 
                              "An error occurred while retrieving property data. Please try again later."}
                          </p>
                        </div>
                      ) : (
                        <div className="card">
                          <div className="card-body">
                            <h6 className="card-subtitle mb-2 text-muted">
                              {propertyAnalysis[property.zpid].source === "Estimated" 
                                ? "⚠️ Estimated Values (Not Actual Data)" 
                                : "Mashvisor Actual Data"}
                            </h6>
                            
                            {propertyAnalysis[property.zpid].traditional_rental && (
                              <div className="mb-2">
                                <strong>Long-Term Rental:</strong> ${propertyAnalysis[property.zpid].traditional_rental}/mo
                                {propertyAnalysis[property.zpid].source === "Estimated" && (
                                  <span className="badge bg-warning text-dark ms-2">Estimate</span>
                                )}
                                {propertyAnalysis[property.zpid].traditional_ROI && (
                                  <span className="ms-2">
                                    <strong>ROI:</strong> {(propertyAnalysis[property.zpid].traditional_ROI * 100).toFixed(1)}%
                                    {propertyAnalysis[property.zpid].source === "Estimated" && (
                                      <span className="badge bg-warning text-dark ms-1">Estimate</span>
                                    )}
                                  </span>
                                )}
                              </div>
                            )}
                            
                            {propertyAnalysis[property.zpid].airbnb_rental && (
                              <div>
                                <strong>Short-Term Rental:</strong> ${propertyAnalysis[property.zpid].airbnb_rental}/mo
                                {propertyAnalysis[property.zpid].source === "Estimated" && (
                                  <span className="badge bg-warning text-dark ms-2">Estimate</span>
                                )}
                                {propertyAnalysis[property.zpid].airbnb_ROI && (
                                  <span className="ms-2">
                                    <strong>ROI:</strong> {(propertyAnalysis[property.zpid].airbnb_ROI * 100).toFixed(1)}%
                                    {propertyAnalysis[property.zpid].source === "Estimated" && (
                                      <span className="badge bg-warning text-dark ms-1">Estimate</span>
                                    )}
                                  </span>
                                )}
                              </div>
                            )}
                            
                            {propertyAnalysis[property.zpid].source === "Estimated" && (
                              <div className="alert alert-warning mt-2 mb-0 py-1 small">
                                <i className="bi bi-exclamation-triangle me-1"></i>
                                These are rough estimates based on market averages, not actual data for this specific property.
                                For exact DSCR calculations, consider consulting local property managers.
                              </div>
                            )}
                          </div>
                        </div>
                      )}
                    </div>
                  )}
                </div>
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
};

export default PropertyList;
