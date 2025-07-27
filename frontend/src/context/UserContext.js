import React, { createContext, useContext, useState, useEffect } from 'react';
import axios from 'axios';
import toast from 'react-hot-toast';

const UserContext = createContext();

export const useUser = () => {
  const context = useContext(UserContext);
  if (!context) {
    throw new Error('useUser must be used within a UserProvider');
  }
  return context;
};

export const UserProvider = ({ children }) => {
  const [userSettings, setUserSettings] = useState({
    salary: 70000,
    monthlyBudget: 100000,
    monthlyTarget: 10000,
    riskProfile: 'moderate',
    targetEqWeight: 0.75,
    maxDrawdown: 0.20,
    rebalThreshold: 5,
    capitalGainsBudget: 0.03,
    liquidityBufferMonths: 6,
    email: 'akshay.nambiar7@gmail.com'
  });

  const [portfolioData, setPortfolioData] = useState(null);
  const [reports, setReports] = useState([]);
  const [loading, setLoading] = useState(false);

  // Load user settings from localStorage
  useEffect(() => {
    const savedSettings = localStorage.getItem('userSettings');
    if (savedSettings) {
      setUserSettings(JSON.parse(savedSettings));
    }
  }, []);

  // Save user settings to localStorage
  useEffect(() => {
    localStorage.setItem('userSettings', JSON.stringify(userSettings));
  }, [userSettings]);

  // Fetch portfolio data
  const fetchPortfolioData = async () => {
    try {
      setLoading(true);
      const response = await axios.get('/api/portfolio-summary');
      setPortfolioData(response.data);
    } catch (error) {
      console.error('Error fetching portfolio data:', error);
      toast.error('Failed to fetch portfolio data');
    } finally {
      setLoading(false);
    }
  };

  // Fetch holdings data
  const fetchHoldings = async () => {
    try {
      const response = await axios.get('/api/holdings');
      return response.data;
    } catch (error) {
      console.error('Error fetching holdings:', error);
      toast.error('Failed to fetch holdings data');
      return [];
    }
  };

  // Fetch daily reports
  const fetchReports = async () => {
    try {
      const response = await axios.get('/api/reports');
      setReports(response.data);
    } catch (error) {
      console.error('Error fetching reports:', error);
      toast.error('Failed to fetch reports');
    }
  };

  // Update user settings
  const updateUserSettings = (newSettings) => {
    setUserSettings(prev => ({ ...prev, ...newSettings }));
    toast.success('Settings updated successfully');
  };

  // Save user settings to backend
  const saveUserSettings = async () => {
    try {
      await axios.post('/api/settings', userSettings);
      toast.success('Settings saved to server');
    } catch (error) {
      console.error('Error saving settings:', error);
      toast.error('Failed to save settings');
    }
  };

  // Auto-refresh data every 5 minutes
  useEffect(() => {
    fetchPortfolioData();
    fetchReports();

    const interval = setInterval(() => {
      fetchPortfolioData();
      fetchReports();
    }, 5 * 60 * 1000); // 5 minutes

    return () => clearInterval(interval);
  }, []);

  const value = {
    userSettings,
    portfolioData,
    reports,
    loading,
    updateUserSettings,
    saveUserSettings,
    fetchPortfolioData,
    fetchHoldings,
    fetchReports
  };

  return (
    <UserContext.Provider value={value}>
      {children}
    </UserContext.Provider>
  );
}; 