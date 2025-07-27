import React, { useState, useEffect } from 'react';
import { useUser } from '../context/UserContext';
import { 
  ChartBarIcon,
  ArrowTrendingUpIcon as TrendingUpIcon,
  ArrowTrendingDownIcon as TrendingDownIcon,
  MagnifyingGlassIcon,
  FunnelIcon
} from '@heroicons/react/24/outline';
import { PieChart, Pie, Cell, ResponsiveContainer, BarChart, Bar, XAxis, YAxis, Tooltip, Legend } from 'recharts';

const Portfolio = () => {
  const { portfolioData, fetchHoldings } = useUser();
  const [holdings, setHoldings] = useState([]);
  const [filteredHoldings, setFilteredHoldings] = useState([]);
  const [searchTerm, setSearchTerm] = useState('');
  const [sortBy, setSortBy] = useState('value');
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const loadHoldings = async () => {
      setLoading(true);
      try {
        const holdingsData = await fetchHoldings();
        setHoldings(holdingsData.holdings || []);
        setFilteredHoldings(holdingsData.holdings || []);
      } catch (error) {
        console.error('Error loading holdings:', error);
      } finally {
        setLoading(false);
      }
    };
    loadHoldings();
  }, []);

  // Filter and sort holdings
  useEffect(() => {
    let filtered = holdings.filter(holding =>
      holding.trading_symbol.toLowerCase().includes(searchTerm.toLowerCase()) ||
      holding.company_name.toLowerCase().includes(searchTerm.toLowerCase())
    );

    // Sort holdings
    filtered.sort((a, b) => {
      switch (sortBy) {
        case 'value':
          return (b.quantity * b.last_price) - (a.quantity * a.last_price);
        case 'pnl':
          return b.pnl - a.pnl;
        case 'pnl_percentage':
          return (b.pnl / (a.quantity * a.average_price)) - (a.pnl / (a.quantity * a.average_price));
        case 'day_change':
          return b.day_change_percentage - a.day_change_percentage;
        default:
          return 0;
      }
    });

    setFilteredHoldings(filtered);
  }, [holdings, searchTerm, sortBy]);

  const getSector = (symbol) => {
    const sectorMap = {
      'RELIANCE': 'Oil & Gas',
      'TCS': 'IT',
      'HDFCBANK': 'Banking',
      'INFY': 'IT',
      'ITC': 'FMCG',
      'ICICIBANK': 'Banking',
      'HINDUNILVR': 'FMCG',
      'SBIN': 'Banking',
      'BHARTIARTL': 'Telecom',
      'KOTAKBANK': 'Banking',
      'AXISBANK': 'Banking',
      'ASIANPAINT': 'Chemicals',
      'MARUTI': 'Automobile',
      'SUNPHARMA': 'Pharmaceuticals',
      'TATAMOTORS': 'Automobile',
      'WIPRO': 'IT',
      'ULTRACEMCO': 'Cement',
      'TITAN': 'Consumer Goods',
      'BAJFINANCE': 'NBFC',
      'NESTLEIND': 'FMCG',
      'POWERGRID': 'Power',
      'NIFTYBEES': 'ETF',
      'GOLDBEES': 'ETF',
      'JUNIORBEES': 'ETF'
    };
    return sectorMap[symbol] || 'Others';
  };

  // Calculate sector allocation
  const sectorAllocation = holdings.reduce((acc, holding) => {
    const sector = getSector(holding.trading_symbol);
    const value = holding.quantity * holding.last_price;
    
    if (!acc[sector]) {
      acc[sector] = { value: 0, count: 0, holdings: [] };
    }
    
    acc[sector].value += value;
    acc[sector].count += 1;
    acc[sector].holdings.push(holding.trading_symbol);
    
    return acc;
  }, {});

  const sectorData = Object.entries(sectorAllocation).map(([sector, data]) => ({
    name: sector,
    value: data.value,
    count: data.count
  }));

  const COLORS = ['#0088FE', '#00C49F', '#FFBB28', '#FF8042', '#8884D8', '#82CA9D'];

  const HoldingRow = ({ holding, index }) => {
    const value = holding.quantity * holding.last_price;
    const pnlPercentage = holding.average_price > 0 ? (holding.pnl / (holding.quantity * holding.average_price)) * 100 : 0;

    return (
      <tr key={index} className="hover:bg-gray-50">
        <td className="px-6 py-4 whitespace-nowrap">
          <div>
            <div className="text-sm font-medium text-gray-900">{holding.trading_symbol}</div>
            <div className="text-sm text-gray-500">{holding.company_name}</div>
          </div>
        </td>
        <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
          {holding.quantity.toLocaleString()}
        </td>
        <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
          ₹{holding.average_price?.toFixed(2)}
        </td>
        <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
          ₹{holding.last_price?.toFixed(2)}
        </td>
        <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
          ₹{value.toLocaleString()}
        </td>
        <td className="px-6 py-4 whitespace-nowrap">
          <div className="text-sm">
            <div className={`font-medium ${holding.pnl > 0 ? 'text-success-600' : 'text-danger-600'}`}>
              {holding.pnl > 0 ? '+' : ''}₹{holding.pnl?.toLocaleString()}
            </div>
            <div className={`text-xs ${pnlPercentage > 0 ? 'text-success-600' : 'text-danger-600'}`}>
              {pnlPercentage > 0 ? '+' : ''}{pnlPercentage.toFixed(2)}%
            </div>
          </div>
        </td>
        <td className="px-6 py-4 whitespace-nowrap">
          <div className="text-sm">
            <div className={`font-medium ${holding.day_change_percentage > 0 ? 'text-success-600' : 'text-danger-600'}`}>
              {holding.day_change_percentage > 0 ? '+' : ''}{holding.day_change_percentage?.toFixed(2)}%
            </div>
            <div className="text-xs text-gray-500">
              ₹{holding.day_change?.toFixed(2)}
            </div>
          </div>
        </td>
      </tr>
    );
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600"></div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div>
        <h1 className="text-3xl font-bold text-gray-900">Portfolio</h1>
        <p className="mt-2 text-gray-600">
          Detailed view of your holdings, sector allocation, and performance metrics.
        </p>
      </div>

      {/* Portfolio Summary Cards */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
        <div className="bg-white rounded-lg shadow p-6">
          <div className="flex items-center">
            <ChartBarIcon className="h-8 w-8 text-primary-600" />
            <div className="ml-4">
              <p className="text-sm font-medium text-gray-600">Total Value</p>
              <p className="text-2xl font-semibold text-gray-900">
                ₹{portfolioData?.total_value?.toLocaleString()}
              </p>
            </div>
          </div>
        </div>
        <div className="bg-white rounded-lg shadow p-6">
          <div className="flex items-center">
            <TrendingUpIcon className="h-8 w-8 text-success-600" />
            <div className="ml-4">
              <p className="text-sm font-medium text-gray-600">Total P&L</p>
              <p className={`text-2xl font-semibold ${
                portfolioData?.total_pnl > 0 ? 'text-success-600' : 'text-danger-600'
              }`}>
                {portfolioData?.total_pnl > 0 ? '+' : ''}₹{portfolioData?.total_pnl?.toLocaleString()}
              </p>
            </div>
          </div>
        </div>
        <div className="bg-white rounded-lg shadow p-6">
          <div className="flex items-center">
            <ChartBarIcon className="h-8 w-8 text-warning-600" />
            <div className="ml-4">
              <p className="text-sm font-medium text-gray-600">Holdings</p>
              <p className="text-2xl font-semibold text-gray-900">{holdings.length}</p>
            </div>
          </div>
        </div>
        <div className="bg-white rounded-lg shadow p-6">
          <div className="flex items-center">
            <TrendingDownIcon className="h-8 w-8 text-danger-600" />
            <div className="ml-4">
              <p className="text-sm font-medium text-gray-600">Avg Return</p>
              <p className="text-2xl font-semibold text-gray-900">
                {portfolioData?.total_value > 0 ? ((portfolioData?.total_pnl / portfolioData?.total_value) * 100).toFixed(2) : 0}%
              </p>
            </div>
          </div>
        </div>
      </div>

      {/* Charts Section */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Sector Allocation Pie Chart */}
        <div className="bg-white rounded-lg shadow p-6">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">Sector Allocation</h3>
          <ResponsiveContainer width="100%" height={300}>
            <PieChart>
              <Pie
                data={sectorData}
                cx="50%"
                cy="50%"
                labelLine={false}
                label={({ name, percent }) => `${name} ${(percent * 100).toFixed(0)}%`}
                outerRadius={80}
                fill="#8884d8"
                dataKey="value"
              >
                {sectorData.map((entry, index) => (
                  <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                ))}
              </Pie>
              <Tooltip formatter={(value) => `₹${value.toLocaleString()}`} />
            </PieChart>
          </ResponsiveContainer>
        </div>

        {/* Top Holdings Bar Chart */}
        <div className="bg-white rounded-lg shadow p-6">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">Top 10 Holdings by Value</h3>
          <ResponsiveContainer width="100%" height={300}>
            <BarChart data={holdings.slice(0, 10).map(h => ({
              name: h.trading_symbol,
              value: h.quantity * h.last_price
            }))}>
              <XAxis dataKey="name" />
              <YAxis />
              <Tooltip formatter={(value) => `₹${value.toLocaleString()}`} />
              <Bar dataKey="value" fill="#3b82f6" />
            </BarChart>
          </ResponsiveContainer>
        </div>
      </div>

      {/* Holdings Table */}
      <div className="bg-white rounded-lg shadow">
        <div className="px-6 py-4 border-b border-gray-200">
          <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between">
            <h3 className="text-lg font-semibold text-gray-900">Holdings</h3>
            <div className="mt-4 sm:mt-0 flex flex-col sm:flex-row gap-4">
              {/* Search */}
              <div className="relative">
                <MagnifyingGlassIcon className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-gray-400" />
                <input
                  type="text"
                  placeholder="Search holdings..."
                  value={searchTerm}
                  onChange={(e) => setSearchTerm(e.target.value)}
                  className="pl-10 pr-4 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-primary-500 focus:border-primary-500"
                />
              </div>
              {/* Sort */}
              <div className="relative">
                <FunnelIcon className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-gray-400" />
                <select
                  value={sortBy}
                  onChange={(e) => setSortBy(e.target.value)}
                  className="pl-10 pr-8 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-primary-500 focus:border-primary-500"
                >
                  <option value="value">Sort by Value</option>
                  <option value="pnl">Sort by P&L</option>
                  <option value="pnl_percentage">Sort by P&L %</option>
                  <option value="day_change">Sort by Day Change</option>
                </select>
              </div>
            </div>
          </div>
        </div>
        <div className="overflow-x-auto">
          <table className="min-w-full divide-y divide-gray-200">
            <thead className="bg-gray-50">
              <tr>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Stock
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Quantity
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Avg Price
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Current Price
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Value
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  P&L
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Day Change
                </th>
              </tr>
            </thead>
            <tbody className="bg-white divide-y divide-gray-200">
              {filteredHoldings.map((holding, index) => (
                <HoldingRow key={index} holding={holding} index={index} />
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
};

export default Portfolio; 