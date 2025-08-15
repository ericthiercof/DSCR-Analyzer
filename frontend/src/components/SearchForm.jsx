import React, { useState } from 'react';
import { useMortgage } from '../context/MortgageContext';

const SearchForm = ({ onSearch, loading, apiConnected }) => {
  const { settings, updateSettings } = useMortgage();
  
  const [searchParams, setSearchParams] = useState({
    city: '',
    state: '',
    downPaymentPercent: 20,
    interestRate: 7.0,
    minPrice: 150000,
    maxPrice: 1500000
  });

  const handleChange = (e) => {
    const { name, value } = e.target;
    setSearchParams(prev => ({
      ...prev,
      [name]: value
    }));
  };

  const handleInterestRateChange = (e) => {
    const rate = parseFloat(e.target.value);
    updateSettings({ interestRate: rate });
    setSearchParams(prev => ({ ...prev, interestRate: rate }));
  };

  const handleDownPaymentChange = (e) => {
    const downPayment = parseFloat(e.target.value);
    // Update the mortgage context with the new down payment percentage
    updateSettings({ downPaymentPercent: downPayment });
    
    // Also update local state
    setSearchParams(prev => ({ ...prev, downPaymentPercent: downPayment }));
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    console.log('Form submitted, preventing default');
    
    // Validate form fields
    if (!searchParams.city.trim()) {
      alert("City is required");
      return;
    }
    
    if (!searchParams.state.trim() || searchParams.state.length !== 2) {
      alert("State must be a valid two-letter code");
      return;
    }
    
    // Convert to snake_case field names that the backend expects
    const processedParams = {
      city: searchParams.city.trim(),
      state: searchParams.state.trim().toUpperCase(),
      // Convert camelCase to snake_case to match backend expectations
      down_payment: parseFloat(searchParams.downPaymentPercent),
      interest_rate: parseFloat(searchParams.interestRate),
      min_price: parseInt(searchParams.minPrice, 10),
      max_price: parseInt(searchParams.maxPrice, 10)
    };
    
    console.log('Form submitting with processed params:', processedParams);
    onSearch(processedParams);
  };

  return (
    <form onSubmit={handleSubmit} className="search-form">
      <h3 className="mb-4">Search Properties</h3>
      
      <div className="mb-3">
        <label htmlFor="city" className="form-label">City</label>
        <input
          type="text"
          className="form-control"
          id="city"
          name="city"
          value={searchParams.city}
          onChange={handleChange}
          required
        />
      </div>
      
      <div className="mb-3">
        <label htmlFor="state" className="form-label">State</label>
        <input
          type="text"
          className="form-control"
          id="state"
          name="state"
          value={searchParams.state}
          onChange={handleChange}
          required
          placeholder="Two-letter state code (e.g., TX)"
        />
        <small className="text-muted">Two-letter state code (e.g., TX)</small>
      </div>
      
      <div className="mb-3">
        <label htmlFor="downPaymentPercent" className="form-label">Down Payment (%)</label>
        <input
          type="number"
          className="form-control"
          id="downPaymentPercent"
          name="downPaymentPercent"
          value={searchParams.downPaymentPercent}
          onChange={handleDownPaymentChange}
          min="0"
          max="100"
        />
      </div>
      
      <div className="mb-3">
        <label htmlFor="interestRate" className="form-label">Interest Rate (%)</label>
        <input
          type="number"
          className="form-control"
          id="interestRate"
          name="interestRate"
          value={searchParams.interestRate}
          onChange={handleInterestRateChange}
          min="0"
          max="20"
          step="0.1"
        />
      </div>
      
      <div className="row mb-3">
        <div className="col">
          <label htmlFor="minPrice" className="form-label">Min Price ($)</label>
          <input
            type="number"
            className="form-control"
            id="minPrice"
            name="minPrice"
            value={searchParams.minPrice}
            onChange={handleChange}
            min="0"
          />
        </div>
        <div className="col">
          <label htmlFor="maxPrice" className="form-label">Max Price ($)</label>
          <input
            type="number"
            className="form-control"
            id="maxPrice"
            name="maxPrice"
            value={searchParams.maxPrice}
            onChange={handleChange}
            min="0"
          />
        </div>
      </div>
      
      <button 
        type="submit" 
        className="btn btn-primary w-100"
        disabled={loading || !apiConnected}
      >
        {loading ? 'Searching...' : 'Search Properties'}
      </button>
    </form>
  );
};

export default SearchForm;