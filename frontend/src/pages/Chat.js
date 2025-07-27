import React, { useState, useEffect, useRef } from 'react';
import { PieChart, Pie, Cell, BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';

const Chat = () => {
  const [messages, setMessages] = useState([]);
  const [inputMessage, setInputMessage] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [insights, setInsights] = useState(null);
  const [showInsights, setShowInsights] = useState(false);
  const messagesEndRef = useRef(null);

  const COLORS = ['#0088FE', '#00C49F', '#FFBB28', '#FF8042', '#8884D8', '#82CA9D'];

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  useEffect(() => {
    // Load chat history on component mount
    loadChatHistory();
    // Load initial insights
    loadInsights();
  }, []);

  const loadChatHistory = async () => {
    try {
      const response = await fetch('/api/chat/history');
      const data = await response.json();
      if (data.history) {
        setMessages(data.history);
      }
    } catch (error) {
      console.error('Error loading chat history:', error);
    }
  };

  const loadInsights = async () => {
    try {
      const response = await fetch('/api/chat/insights');
      const data = await response.json();
      if (data && !data.error) {
        setInsights(data);
      }
    } catch (error) {
      console.error('Error loading insights:', error);
    }
  };

  const sendMessage = async () => {
    if (!inputMessage.trim()) return;

    const userMessage = {
      role: 'user',
      content: inputMessage,
      timestamp: new Date().toISOString()
    };

    setMessages(prev => [...prev, userMessage]);
    setInputMessage('');
    setIsLoading(true);

    try {
      const response = await fetch('/api/chat', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ message: inputMessage }),
      });

      const data = await response.json();
      
      if (data.response) {
        const aiMessage = {
          role: 'assistant',
          content: data.response,
          timestamp: data.timestamp,
          metadata: {
            context_used: data.context_used,
            portfolio_summary: data.portfolio_summary,
            risk_metrics: data.risk_metrics
          }
        };
        setMessages(prev => [...prev, aiMessage]);
      } else {
        throw new Error(data.error || 'Failed to get response');
      }
    } catch (error) {
      console.error('Error sending message:', error);
      const errorMessage = {
        role: 'assistant',
        content: `I apologize, but I encountered an error: ${error.message}. Please try again.`,
        timestamp: new Date().toISOString(),
        isError: true
      };
      setMessages(prev => [...prev, errorMessage]);
    } finally {
      setIsLoading(false);
    }
  };

  const clearChat = async () => {
    try {
      await fetch('/api/chat/clear', { method: 'POST' });
      setMessages([]);
    } catch (error) {
      console.error('Error clearing chat:', error);
    }
  };

  const handleKeyPress = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      sendMessage();
    }
  };

  const formatMessage = (content) => {
    return (
      <ReactMarkdown 
        remarkPlugins={[remarkGfm]}
        components={{
          // Custom styling for different markdown elements
          h1: ({node, ...props}) => <h1 className="text-2xl font-bold text-gray-900 mb-4 mt-6" {...props} />,
          h2: ({node, ...props}) => <h2 className="text-xl font-bold text-gray-800 mb-3 mt-5" {...props} />,
          h3: ({node, ...props}) => <h3 className="text-lg font-semibold text-gray-800 mb-2 mt-4" {...props} />,
          h4: ({node, ...props}) => <h4 className="text-base font-semibold text-gray-700 mb-2 mt-3" {...props} />,
          h5: ({node, ...props}) => <h5 className="text-sm font-semibold text-gray-700 mb-1 mt-2" {...props} />,
          h6: ({node, ...props}) => <h6 className="text-xs font-semibold text-gray-600 mb-1 mt-2" {...props} />,
          p: ({node, ...props}) => <p className="mb-3 text-gray-700 leading-relaxed" {...props} />,
          ul: ({node, ...props}) => <ul className="list-disc list-inside mb-3 space-y-1" {...props} />,
          ol: ({node, ...props}) => <ol className="list-decimal list-inside mb-3 space-y-1" {...props} />,
          li: ({node, ...props}) => <li className="text-gray-700" {...props} />,
          strong: ({node, ...props}) => <strong className="font-bold text-gray-900" {...props} />,
          em: ({node, ...props}) => <em className="italic text-gray-800" {...props} />,
          code: ({node, inline, ...props}) => 
            inline ? 
              <code className="bg-gray-100 text-gray-800 px-1 py-0.5 rounded text-sm font-mono" {...props} /> :
              <code className="block bg-gray-100 text-gray-800 p-3 rounded text-sm font-mono overflow-x-auto" {...props} />,
          pre: ({node, ...props}) => <pre className="bg-gray-100 p-3 rounded-lg overflow-x-auto mb-3" {...props} />,
          blockquote: ({node, ...props}) => <blockquote className="border-l-4 border-blue-500 pl-4 italic text-gray-600 mb-3" {...props} />,
          table: ({node, ...props}) => <table className="min-w-full border border-gray-300 mb-3" {...props} />,
          thead: ({node, ...props}) => <thead className="bg-gray-50" {...props} />,
          tbody: ({node, ...props}) => <tbody {...props} />,
          tr: ({node, ...props}) => <tr className="border-b border-gray-300" {...props} />,
          th: ({node, ...props}) => <th className="px-3 py-2 text-left font-semibold text-gray-700" {...props} />,
          td: ({node, ...props}) => <td className="px-3 py-2 text-gray-700" {...props} />,
          hr: ({node, ...props}) => <hr className="border-gray-300 my-4" {...props} />,
        }}
      >
        {content}
      </ReactMarkdown>
    );
  };

  const getSectorData = () => {
    if (!insights?.sector_analysis) return [];
    
    return Object.entries(insights.sector_analysis).map(([sector, data]) => ({
      name: sector,
      value: data.weight * 100,
      return: data.return * 100,
      count: data.count
    }));
  };

  const getRiskMetrics = () => {
    if (!insights?.risk_metrics) return null;
    
    const metrics = insights.risk_metrics;
    return [
      { name: 'Concentration Risk', value: metrics.concentration_risk * 100, color: metrics.concentration_risk > 0.05 ? '#ff4444' : '#00C49F' },
      { name: 'Sector Concentration', value: metrics.max_sector_weight * 100, color: metrics.max_sector_weight > 0.25 ? '#ff8800' : '#00C49F' },
      { name: 'Portfolio Beta', value: metrics.portfolio_beta, color: '#0088FE' },
      { name: 'Risk Score', value: metrics.risk_score * 100, color: metrics.risk_score > 0.7 ? '#ff4444' : metrics.risk_score > 0.4 ? '#ff8800' : '#00C49F' }
    ];
  };

  const suggestedQuestions = [
    "What are the main risks in my current portfolio?",
    "How can I improve my sector diversification?",
    "Which stocks should I consider selling?",
    "What's the best time to buy more of my top holdings?",
    "How does my portfolio compare to the market?",
    "What are the tax implications of my current positions?",
    "Should I rebalance my portfolio now?",
    "What are the growth prospects for my holdings?"
  ];

  return (
    <div className="min-h-screen bg-gray-50">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div className="bg-white rounded-lg shadow-lg overflow-hidden">
          {/* Header */}
          <div className="bg-gradient-to-r from-blue-600 to-purple-600 px-6 py-4">
            <div className="flex items-center justify-between">
              <div>
                <h1 className="text-2xl font-bold text-white">Portfolio AI Assistant</h1>
                <p className="text-blue-100">Ask me anything about your portfolio and get AI-powered insights</p>
              </div>
              <div className="flex space-x-2">
                <button
                  onClick={() => setShowInsights(!showInsights)}
                  className="bg-white bg-opacity-20 hover:bg-opacity-30 text-white px-4 py-2 rounded-lg transition-colors"
                >
                  {showInsights ? 'Hide Insights' : 'Show Insights'}
                </button>
                <button
                  onClick={clearChat}
                  className="bg-white bg-opacity-20 hover:bg-opacity-30 text-white px-4 py-2 rounded-lg transition-colors"
                >
                  Clear Chat
                </button>
              </div>
            </div>
          </div>

          <div className="flex h-[600px]">
            {/* Insights Panel */}
            {showInsights && (
              <div className="w-1/3 border-r border-gray-200 bg-gray-50 overflow-y-auto">
                <div className="p-4">
                  <h3 className="text-lg font-semibold mb-4">Portfolio Insights</h3>
                  
                  {insights && (
                    <>
                      {/* Portfolio Summary */}
                      <div className="bg-white rounded-lg p-4 mb-4 shadow-sm">
                        <h4 className="font-semibold mb-2">Portfolio Summary</h4>
                        <div className="space-y-1 text-sm">
                          <div>Total Value: ₹{insights.portfolio_summary?.total_value?.toLocaleString() || 'N/A'}</div>
                          <div>Total P&L: ₹{insights.portfolio_summary?.total_pnl?.toLocaleString() || 'N/A'}</div>
                          <div>Holdings: {insights.portfolio_summary?.total_stocks || 'N/A'}</div>
                        </div>
                      </div>

                      {/* Risk Metrics */}
                      <div className="bg-white rounded-lg p-4 mb-4 shadow-sm">
                        <h4 className="font-semibold mb-2">Risk Metrics</h4>
                        <div className="space-y-2">
                          {getRiskMetrics()?.map((metric, index) => (
                            <div key={index} className="flex justify-between items-center">
                              <span className="text-sm">{metric.name}:</span>
                              <span 
                                className="text-sm font-semibold"
                                style={{ color: metric.color }}
                              >
                                {metric.value.toFixed(1)}%
                              </span>
                            </div>
                          ))}
                        </div>
                      </div>

                      {/* Sector Allocation */}
                      <div className="bg-white rounded-lg p-4 mb-4 shadow-sm">
                        <h4 className="font-semibold mb-2">Sector Allocation</h4>
                        <ResponsiveContainer width="100%" height={200}>
                          <PieChart>
                            <Pie
                              data={getSectorData()}
                              cx="50%"
                              cy="50%"
                              labelLine={false}
                              label={({ name, percent }) => `${name} ${(percent * 100).toFixed(0)}%`}
                              outerRadius={80}
                              fill="#8884d8"
                              dataKey="value"
                            >
                              {getSectorData().map((entry, index) => (
                                <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                              ))}
                            </Pie>
                            <Tooltip />
                          </PieChart>
                        </ResponsiveContainer>
                      </div>

                      {/* Recommendations */}
                      {insights.recommendations && insights.recommendations.length > 0 && (
                        <div className="bg-white rounded-lg p-4 mb-4 shadow-sm">
                          <h4 className="font-semibold mb-2">Recommendations</h4>
                          <div className="space-y-2">
                            {insights.recommendations.map((rec, index) => (
                              <div key={index} className="text-sm p-2 bg-yellow-50 rounded border-l-4 border-yellow-400">
                                <div className="font-semibold text-yellow-800">{rec.title}</div>
                                <div className="text-yellow-700">{rec.description}</div>
                              </div>
                            ))}
                          </div>
                        </div>
                      )}

                      {/* Alerts */}
                      {insights.alerts && insights.alerts.length > 0 && (
                        <div className="bg-white rounded-lg p-4 shadow-sm">
                          <h4 className="font-semibold mb-2">Alerts</h4>
                          <div className="space-y-2">
                            {insights.alerts.map((alert, index) => (
                              <div key={index} className={`text-sm p-2 rounded border-l-4 ${
                                alert.severity === 'warning' ? 'bg-red-50 border-red-400' : 'bg-blue-50 border-blue-400'
                              }`}>
                                <div className="font-semibold">{alert.message}</div>
                              </div>
                            ))}
                          </div>
                        </div>
                      )}
                    </>
                  )}
                </div>
              </div>
            )}

            {/* Chat Area */}
            <div className={`flex-1 flex flex-col ${showInsights ? 'w-2/3' : 'w-full'}`}>
              {/* Messages */}
              <div className="flex-1 overflow-y-auto p-4 space-y-4">
                {messages.length === 0 && (
                  <div className="text-center text-gray-500 py-8">
                    <div className="text-4xl mb-4">🤖</div>
                    <h3 className="text-lg font-semibold mb-2">Welcome to Portfolio AI Assistant</h3>
                    <p className="mb-6">Ask me anything about your portfolio, market analysis, or investment strategies.</p>
                    
                    {/* Suggested Questions */}
                    <div className="grid grid-cols-1 gap-2 max-w-md mx-auto">
                      <p className="text-sm font-semibold text-gray-600 mb-2">Try asking:</p>
                      {suggestedQuestions.map((question, index) => (
                        <button
                          key={index}
                          onClick={() => setInputMessage(question)}
                          className="text-left p-3 bg-gray-100 hover:bg-gray-200 rounded-lg text-sm transition-colors"
                        >
                          {question}
                        </button>
                      ))}
                    </div>
                  </div>
                )}

                {messages.map((message, index) => (
                  <div
                    key={index}
                    className={`flex ${message.role === 'user' ? 'justify-end' : 'justify-start'}`}
                  >
                    <div
                      className={`max-w-3xl rounded-lg px-4 py-2 ${
                        message.role === 'user'
                          ? 'bg-blue-600 text-white'
                          : message.isError
                          ? 'bg-red-100 text-red-800 border border-red-200'
                          : 'bg-gray-100 text-gray-800'
                      }`}
                    >
                      <div className="prose prose-sm max-w-none">
                        {formatMessage(message.content)}
                      </div>
                      
                      {message.metadata && message.role === 'assistant' && (
                        <div className="mt-2 pt-2 border-t border-gray-200 text-xs text-gray-500">
                          <div>Context used: {message.metadata.context_used?.join(', ') || 'N/A'}</div>
                          {message.metadata.portfolio_summary && (
                            <div>Portfolio value: ₹{message.metadata.portfolio_summary.total_value?.toLocaleString() || 'N/A'}</div>
                          )}
                        </div>
                      )}
                    </div>
                  </div>
                ))}

                {isLoading && (
                  <div className="flex justify-start">
                    <div className="bg-gray-100 rounded-lg px-4 py-2">
                      <div className="flex items-center space-x-2">
                        <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-blue-600"></div>
                        <span className="text-gray-600">AI is analyzing your portfolio...</span>
                      </div>
                    </div>
                  </div>
                )}

                <div ref={messagesEndRef} />
              </div>

              {/* Input Area */}
              <div className="border-t border-gray-200 p-4">
                <div className="flex space-x-2">
                  <textarea
                    value={inputMessage}
                    onChange={(e) => setInputMessage(e.target.value)}
                    onKeyPress={handleKeyPress}
                    placeholder="Ask me about your portfolio, market analysis, or investment strategies..."
                    className="flex-1 border border-gray-300 rounded-lg px-3 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent resize-none"
                    rows="2"
                    disabled={isLoading}
                  />
                  <button
                    onClick={sendMessage}
                    disabled={isLoading || !inputMessage.trim()}
                    className="bg-blue-600 hover:bg-blue-700 disabled:bg-gray-400 text-white px-6 py-2 rounded-lg transition-colors"
                  >
                    Send
                  </button>
                </div>
                <div className="text-xs text-gray-500 mt-2">
                  Press Enter to send, Shift+Enter for new line
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Chat; 