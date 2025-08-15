import React, { createContext, useContext, useState } from 'react';

// Default settings
const defaultSettings = {
  interestRate: 7.0,
  downPaymentPercent: 20,
  loanTermYears: 30
};

// Create context
const MortgageContext = createContext(null);

// Provider component
export const MortgageProvider = ({ children }) => {
  const [settings, setSettings] = useState(defaultSettings);

  // Function to update settings
  const updateSettings = (newSettings) => {
    console.log("Mortgage settings updated:", newSettings);
    setSettings(prev => ({ ...prev, ...newSettings }));
  };

  return (
    <MortgageContext.Provider value={{ settings, updateSettings }}>
      {children}
    </MortgageContext.Provider>
  );
};

// Hook for components to use
export const useMortgage = () => {
  const context = useContext(MortgageContext);
  if (!context) {
    throw new Error('useMortgage must be used within a MortgageProvider');
  }
  return context;
};
