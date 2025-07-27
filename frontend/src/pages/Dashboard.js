import React, { useEffect, useState } from 'react';
import { useUser } from '../context/UserContext';
import { 
  CurrencyDollarIcon as CurrencyRupeeIcon, 
  ArrowTrendingUpIcon as TrendingUpIcon, 
  ArrowTrendingDownIcon as TrendingDownIcon,
  ChartBarIcon,
  ClockIcon,
  CheckCircleIcon
} from '@heroicons/react/24/outline';
import { format } from 'date-fns';

const Dashboard = () => {
  const { 
    userSettings, 
    portfolioData, 
    reports, 
    loading,
    fetchPortfolioData,
    fetchReports,
    fetchHoldings
  } = useUser();

  const [holdings, setHoldings] = useState([]);

  useEffect(() => {
    const loadHoldings = async () => {
      const holdingsData = await fetchHoldings();
      setHoldings(holdingsData.holdings || []);
    };
    loadHoldings();
  }, [fetchHoldings]);

  const StatCard = ({ title, value, change, icon: Icon, color = 'primary' }) => (
    <div className="bg-white rounded-lg shadow p-6">
      <div className="flex items-center">
        <div className={`p-2 rounded-lg bg-${color}-100`}>
          <Icon className={`h-6 w-6 text-${color}-600`} />
        </div>
        <div className="ml-4">
          <p className="text-sm font-medium text-gray-600">{title}</p>
          <p className="text-2xl font-semibold text-gray-900">{value}</p>
          {change && (
            <div className="flex items-center mt-1">
              {change > 0 ? (
                <TrendingUpIcon className="h-4 w-4 text-success-500" />
              ) : (
                <TrendingDownIcon className="h-4 w-4 text-danger-500" />
              )}
              <span className={`ml-1 text-sm font-medium ${
                change > 0 ? 'text-success-600' : 'text-danger-600'
              }`}>
                {change > 0 ? '+' : ''}{change}%
              </span>
            </div>
          )}
        </div>
      </div>
    </div>
  );

  const RecentReport = ({ report }) => (
    <div className="bg-white rounded-lg shadow p-6">
      <div className="flex items-center justify-between mb-4">
        <h3 className="text-lg font-semibold text-gray-900">
          {format(new Date(report.date), 'MMM dd, yyyy')}
        </h3>
        <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-success-100 text-success-800">
          <CheckCircleIcon className="h-4 w-4 mr-1" />
          Completed
        </span>
      </div>
      
      <div className="space-y-3">
        <div className="flex justify-between">
          <span className="text-sm text-gray-600">Recommendations:</span>
          <span className="text-sm font-medium">{report.recommendations_count || 0}</span>
        </div>
        <div className="flex justify-between">
          <span className="text-sm text-gray-600">Executed:</span>
          <span className="text-sm font-medium">{report.executed_count || 0}</span>
        </div>
        <div className="flex justify-between">
          <span className="text-sm text-gray-600">Portfolio Return:</span>
          <span className={`text-sm font-medium ${
            (report.portfolio_return || 0) > 0 ? 'text-success-600' : 'text-danger-600'
          }`}>
            {(report.portfolio_return || 0).toFixed(2)}%
          </span>
        </div>
      </div>
    </div>
  );

  const TopHoldings = () => (
    <div className="bg-white rounded-lg shadow">
      <div className="px-6 py-4 border-b border-gray-200">
        <h3 className="text-lg font-semibold text-gray-900">Top Holdings</h3>
      </div>
      <div className="divide-y divide-gray-200">
        {holdings.slice(0, 5).map((holding, index) => (
          <div key={index} className="px-6 py-4">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-gray-900">{holding.trading_symbol}</p>
                <p className="text-sm text-gray-500">{holding.company_name}</p>
              </div>
              <div className="text-right">
                <p className="text-sm font-medium text-gray-900">
                  ₹{(holding.quantity * holding.last_price).toLocaleString()}
                </p>
                <p className={`text-sm ${
                  holding.pnl > 0 ? 'text-success-600' : 'text-danger-600'
                }`}>
                  {holding.pnl > 0 ? '+' : ''}₹{holding.pnl.toLocaleString()}
                </p>
              </div>
            </div>
          </div>
        ))}
      </div>
    </div>
  );

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
        <h1 className="text-3xl font-bold text-gray-900">Dashboard</h1>
        <p className="mt-2 text-gray-600">
          Welcome back! Here's your portfolio overview and recent activity.
        </p>
      </div>

      {/* Stats Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        <StatCard
          title="Portfolio Value"
          value={portfolioData ? `₹${portfolioData.total_value?.toLocaleString()}` : '₹0'}
          change={portfolioData?.daily_return}
          icon={CurrencyRupeeIcon}
          color="primary"
        />
        <StatCard
          title="Total P&L"
          value={portfolioData ? `₹${portfolioData.total_pnl?.toLocaleString()}` : '₹0'}
          change={portfolioData?.pnl_percentage}
          icon={ChartBarIcon}
          color={portfolioData?.total_pnl > 0 ? 'success' : 'danger'}
        />
        <StatCard
          title="Monthly Target"
          value={`₹${userSettings.monthlyTarget?.toLocaleString()}`}
          icon={TrendingUpIcon}
          color="warning"
        />
        <StatCard
          title="Holdings"
          value={portfolioData?.total_stocks || 0}
          icon={ChartBarIcon}
          color="primary"
        />
      </div>

      {/* Main Content Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Recent Reports */}
        <div className="lg:col-span-2">
          <div className="bg-white rounded-lg shadow">
            <div className="px-6 py-4 border-b border-gray-200">
              <h3 className="text-lg font-semibold text-gray-900">Recent Reports</h3>
            </div>
            <div className="p-6">
              {reports.length > 0 ? (
                <div className="space-y-4">
                  {reports.slice(0, 3).map((report, index) => (
                    <RecentReport key={index} report={report} />
                  ))}
                </div>
              ) : (
                <div className="text-center py-8">
                  <ClockIcon className="mx-auto h-12 w-12 text-gray-400" />
                  <h3 className="mt-2 text-sm font-medium text-gray-900">No reports yet</h3>
                  <p className="mt-1 text-sm text-gray-500">
                    Daily reports will appear here after the first Airflow run.
                  </p>
                </div>
              )}
            </div>
          </div>
        </div>

        {/* Top Holdings */}
        <div>
          <TopHoldings />
        </div>
      </div>

      {/* User Settings Summary */}
      <div className="bg-white rounded-lg shadow p-6">
        <h3 className="text-lg font-semibold text-gray-900 mb-4">Investment Goals</h3>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <div>
            <p className="text-sm text-gray-600">Monthly Salary</p>
            <p className="text-lg font-semibold">₹{userSettings.salary?.toLocaleString()}</p>
          </div>
          <div>
            <p className="text-sm text-gray-600">Monthly Budget</p>
            <p className="text-lg font-semibold">₹{userSettings.monthlyBudget?.toLocaleString()}</p>
          </div>
          <div>
            <p className="text-sm text-gray-600">Risk Profile</p>
            <p className="text-lg font-semibold capitalize">{userSettings.riskProfile}</p>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Dashboard; 