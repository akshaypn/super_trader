import React, { useState } from 'react';
import { useUser } from '../context/UserContext';
import { 
  DocumentTextIcon,
  CalendarIcon,
  ChartBarIcon,
  CheckCircleIcon,
  XCircleIcon,
  ClockIcon
} from '@heroicons/react/24/outline';
import { format } from 'date-fns';

const Reports = () => {
  const { reports, loading } = useUser();
  const [selectedReport, setSelectedReport] = useState(null);

  const ReportCard = ({ report, onClick }) => (
    <div 
      className="bg-white rounded-lg shadow p-6 cursor-pointer hover:shadow-lg transition-shadow"
      onClick={() => onClick(report)}
    >
      <div className="flex items-center justify-between mb-4">
        <div className="flex items-center">
          <CalendarIcon className="h-5 w-5 text-gray-400 mr-2" />
          <h3 className="text-lg font-semibold text-gray-900">
            {format(new Date(report.date), 'MMM dd, yyyy')}
          </h3>
        </div>
        <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-success-100 text-success-800">
          <CheckCircleIcon className="h-4 w-4 mr-1" />
          Completed
        </span>
      </div>
      
      <div className="grid grid-cols-2 gap-4 text-sm">
        <div>
          <p className="text-gray-600">Portfolio Value</p>
          <p className="font-semibold">₹{report.total_value?.toLocaleString()}</p>
        </div>
        <div>
          <p className="text-gray-600">Total P&L</p>
          <p className={`font-semibold ${
            report.total_pnl > 0 ? 'text-success-600' : 'text-danger-600'
          }`}>
            {report.total_pnl > 0 ? '+' : ''}₹{report.total_pnl?.toLocaleString()}
          </p>
        </div>
        <div>
          <p className="text-gray-600">Recommendations</p>
          <p className="font-semibold">{report.recommendations_count || 0}</p>
        </div>
        <div>
          <p className="text-gray-600">Portfolio Return</p>
          <p className={`font-semibold ${
            (report.portfolio_return || 0) > 0 ? 'text-success-600' : 'text-danger-600'
          }`}>
            {(report.portfolio_return || 0).toFixed(2)}%
          </p>
        </div>
      </div>
    </div>
  );

  const ReportDetail = ({ report, onClose }) => (
    <div className="fixed inset-0 bg-gray-600 bg-opacity-50 overflow-y-auto h-full w-full z-50">
      <div className="relative top-20 mx-auto p-5 border w-11/12 max-w-4xl shadow-lg rounded-md bg-white">
        <div className="flex justify-between items-center mb-6">
          <h2 className="text-2xl font-bold text-gray-900">
            Portfolio Report - {format(new Date(report.date), 'MMMM dd, yyyy')}
          </h2>
          <button
            onClick={onClose}
            className="text-gray-400 hover:text-gray-600"
          >
            <XCircleIcon className="h-6 w-6" />
          </button>
        </div>

        <div className="space-y-6">
          {/* Portfolio Summary */}
          <div className="bg-gray-50 rounded-lg p-6">
            <h3 className="text-lg font-semibold text-gray-900 mb-4">Portfolio Summary</h3>
            <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
              <div>
                <p className="text-sm text-gray-600">Total Value</p>
                <p className="text-lg font-semibold">₹{report.total_value?.toLocaleString()}</p>
              </div>
              <div>
                <p className="text-sm text-gray-600">Total P&L</p>
                <p className={`text-lg font-semibold ${
                  report.total_pnl > 0 ? 'text-success-600' : 'text-danger-600'
                }`}>
                  {report.total_pnl > 0 ? '+' : ''}₹{report.total_pnl?.toLocaleString()}
                </p>
              </div>
              <div>
                <p className="text-sm text-gray-600">Holdings</p>
                <p className="text-lg font-semibold">{report.total_stocks || 0}</p>
              </div>
              <div>
                <p className="text-sm text-gray-600">Return</p>
                <p className={`text-lg font-semibold ${
                  (report.portfolio_return || 0) > 0 ? 'text-success-600' : 'text-danger-600'
                }`}>
                  {(report.portfolio_return || 0).toFixed(2)}%
                </p>
              </div>
            </div>
          </div>

          {/* Performance Metrics */}
          {report.alpha !== undefined && (
            <div className="bg-gray-50 rounded-lg p-6">
              <h3 className="text-lg font-semibold text-gray-900 mb-4">Performance Metrics</h3>
              <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                <div>
                  <p className="text-sm text-gray-600">Alpha</p>
                  <p className={`text-lg font-semibold ${
                    (report.alpha || 0) > 0 ? 'text-success-600' : 'text-danger-600'
                  }`}>
                    {(report.alpha || 0).toFixed(2)}%
                  </p>
                </div>
                <div>
                  <p className="text-sm text-gray-600">Beta</p>
                  <p className="text-lg font-semibold">{(report.beta || 1.0).toFixed(2)}</p>
                </div>
                <div>
                  <p className="text-sm text-gray-600">Sharpe Ratio</p>
                  <p className="text-lg font-semibold">{(report.sharpe_ratio || 0).toFixed(2)}</p>
                </div>
                <div>
                  <p className="text-sm text-gray-600">Win Rate</p>
                  <p className="text-lg font-semibold">{(report.win_rate || 0).toFixed(1)}%</p>
                </div>
              </div>
            </div>
          )}

          {/* Recommendations */}
          <div className="bg-gray-50 rounded-lg p-6">
            <h3 className="text-lg font-semibold text-gray-900 mb-4">Trade Recommendations</h3>
            {report.recommendations && report.recommendations.length > 0 ? (
              <div className="space-y-4">
                {report.recommendations.map((rec, index) => (
                  <div key={index} className="bg-white rounded-lg p-4 border">
                    <div className="flex items-center justify-between mb-2">
                      <div className="flex items-center">
                        <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${
                          rec.action === 'BUY' 
                            ? 'bg-success-100 text-success-800'
                            : rec.action === 'SELL'
                            ? 'bg-danger-100 text-danger-800'
                            : 'bg-warning-100 text-warning-800'
                        }`}>
                          {rec.action}
                        </span>
                        <span className="ml-2 font-semibold">{rec.symbol}</span>
                      </div>
                      <span className="text-sm text-gray-500">
                        Confidence: {(rec.confidence * 100).toFixed(0)}%
                      </span>
                    </div>
                    <div className="grid grid-cols-2 md:grid-cols-4 gap-4 text-sm">
                      <div>
                        <p className="text-gray-600">Quantity</p>
                        <p className="font-medium">{rec.quantity}</p>
                      </div>
                      <div>
                        <p className="text-gray-600">Limit Price</p>
                        <p className="font-medium">₹{rec.limit_price}</p>
                      </div>
                      <div>
                        <p className="text-gray-600">Value</p>
                        <p className="font-medium">₹{(rec.quantity * rec.limit_price).toLocaleString()}</p>
                      </div>
                      <div>
                        <p className="text-gray-600">Status</p>
                        <p className="font-medium capitalize">{rec.status || 'pending'}</p>
                      </div>
                    </div>
                    <p className="text-sm text-gray-600 mt-2">{rec.rationale}</p>
                  </div>
                ))}
              </div>
            ) : (
              <p className="text-gray-500">No recommendations for this date.</p>
            )}
          </div>

          {/* Market Context */}
          {report.market_context && (
            <div className="bg-gray-50 rounded-lg p-6">
              <h3 className="text-lg font-semibold text-gray-900 mb-4">Market Context</h3>
              <div className="grid grid-cols-2 md:grid-cols-3 gap-4">
                <div>
                  <p className="text-sm text-gray-600">Nifty 50</p>
                  <p className="font-semibold">₹{report.market_context.nifty_50?.toLocaleString()}</p>
                </div>
                <div>
                  <p className="text-sm text-gray-600">USD/INR</p>
                  <p className="font-semibold">₹{report.market_context.usd_inr}</p>
                </div>
                <div>
                  <p className="text-sm text-gray-600">VIX</p>
                  <p className="font-semibold">{report.market_context.vix?.toFixed(2)}</p>
                </div>
              </div>
            </div>
          )}
        </div>
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
        <h1 className="text-3xl font-bold text-gray-900">Daily Reports</h1>
        <p className="mt-2 text-gray-600">
          View your daily portfolio analysis and AI recommendations from the Airflow pipeline.
        </p>
      </div>

      {/* Reports Grid */}
      {reports.length > 0 ? (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {reports.map((report, index) => (
            <ReportCard
              key={index}
              report={report}
              onClick={setSelectedReport}
            />
          ))}
        </div>
      ) : (
        <div className="text-center py-12">
          <ClockIcon className="mx-auto h-12 w-12 text-gray-400" />
          <h3 className="mt-2 text-sm font-medium text-gray-900">No reports available</h3>
          <p className="mt-1 text-sm text-gray-500">
            Daily reports will appear here after the Airflow pipeline runs.
          </p>
        </div>
      )}

      {/* Report Detail Modal */}
      {selectedReport && (
        <ReportDetail
          report={selectedReport}
          onClose={() => setSelectedReport(null)}
        />
      )}
    </div>
  );
};

export default Reports; 