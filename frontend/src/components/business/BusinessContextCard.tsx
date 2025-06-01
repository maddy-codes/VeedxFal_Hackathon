'use client';

import { useState, useEffect } from 'react';
import { Building2, TrendingUp, DollarSign, Package, Users, AlertCircle, CheckCircle, Clock, Lightbulb } from 'lucide-react';

interface BusinessSummary {
  executive_summary: string;
  key_insights: string[];
  performance_highlights: string[];
  areas_for_improvement: string[];
  strategic_recommendations: string[];
  market_outlook: string;
  priority_actions: string[];
  generated_at: string;
  ai_provider: string;
}

interface BusinessData {
  store_name: string;
  total_products: number;
  revenue_30d: number;
  orders_30d: number;
  avg_order_value: number;
}

interface TrendSummary {
  total_products: number;
  summary: {
    Hot: number;
    Rising: number;
    Steady: number;
    Declining: number;
  };
  percentages: {
    Hot: number;
    Rising: number;
    Steady: number;
    Declining: number;
  };
  average_scores: {
    google_trend_index: number;
    social_score: number;
    final_score: number;
  };
}

interface BusinessContextData {
  shop_id: number;
  business_summary: BusinessSummary;
  trend_summary: TrendSummary;
  business_data: BusinessData;
  generated_at: string;
}

interface BusinessContextCardProps {
  shopId: number;
}

export function BusinessContextCard({ shopId }: BusinessContextCardProps) {
  const [contextData, setContextData] = useState<BusinessContextData | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [expandedSection, setExpandedSection] = useState<string | null>('summary');

  useEffect(() => {
    fetchBusinessContext();
  }, [shopId]);

  const fetchBusinessContext = async () => {
    try {
      setLoading(true);
      setError(null);

      // Try streaming endpoint first
      try {
        const response = await fetch(`http://localhost:8000/api/v1/trend-analysis/business-context-stream/${shopId}`, {
          headers: {
            'Authorization': `Bearer ${localStorage.getItem('access_token')}`,
            'Accept': 'text/event-stream',
          },
        });

        if (!response.ok) {
          throw new Error(`Streaming failed: ${response.statusText}`);
        }

        const reader = response.body?.getReader();
        const decoder = new TextDecoder();

        if (reader) {
          while (true) {
            const { done, value } = await reader.read();
            if (done) break;

            const chunk = decoder.decode(value);
            const lines = chunk.split('\n');

            for (const line of lines) {
              if (line.startsWith('data: ')) {
                try {
                  const data = JSON.parse(line.slice(6));
                  
                  if (data.type === 'status') {
                    // Update loading message
                    console.log('Status:', data.message);
                  } else if (data.type === 'complete') {
                    // Set the complete data
                    setContextData(data.data);
                    setLoading(false);
                    return;
                  } else if (data.type === 'error') {
                    throw new Error(data.message);
                  }
                } catch (parseError) {
                  console.warn('Failed to parse streaming data:', parseError);
                }
              }
            }
          }
        }
      } catch (streamError) {
        console.warn('Streaming failed, falling back to regular API:', streamError);
        
        // Fallback to regular API
        const response = await fetch(`http://localhost:8000/api/v1/trend-analysis/business-context/${shopId}`, {
          headers: {
            'Authorization': `Bearer ${localStorage.getItem('access_token')}`,
            'Content-Type': 'application/json',
          },
        });

        if (!response.ok) {
          throw new Error(`Failed to fetch business context: ${response.statusText}`);
        }

        const data = await response.json();
        setContextData(data);
      }
    } catch (err) {
      console.error('Error fetching business context:', err);
      setError(err instanceof Error ? err.message : 'Failed to load business context');
    } finally {
      setLoading(false);
    }
  };

  const formatCurrency = (amount: number) => {
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: 'USD',
      minimumFractionDigits: 0,
      maximumFractionDigits: 0,
    }).format(amount);
  };

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleString('en-US', {
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit',
    });
  };

  const toggleSection = (section: string) => {
    setExpandedSection(expandedSection === section ? null : section);
  };

  if (loading) {
    return (
      <div className="bg-white rounded-lg shadow-lg p-6">
        <div className="animate-pulse">
          <div className="flex items-center space-x-3 mb-4">
            <div className="w-8 h-8 bg-gray-200 rounded"></div>
            <div className="h-6 bg-gray-200 rounded w-48"></div>
          </div>
          <div className="space-y-3">
            <div className="h-4 bg-gray-200 rounded w-full"></div>
            <div className="h-4 bg-gray-200 rounded w-3/4"></div>
            <div className="h-4 bg-gray-200 rounded w-1/2"></div>
          </div>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="bg-white rounded-lg shadow-lg p-6">
        <div className="flex items-center space-x-3 text-red-600 mb-4">
          <AlertCircle className="h-6 w-6" />
          <h3 className="text-lg font-semibold">Business Context Error</h3>
        </div>
        <p className="text-gray-600 mb-4">{error}</p>
        <button
          onClick={fetchBusinessContext}
          className="px-4 py-2 bg-primary text-white rounded-md hover:bg-primary/90 transition-colors"
        >
          Retry
        </button>
      </div>
    );
  }

  if (!contextData) {
    return null;
  }

  const { business_summary, business_data, trend_summary } = contextData;

  return (
    <div className="bg-gradient-to-br from-blue-50 to-indigo-50 rounded-lg shadow-lg overflow-hidden">
      {/* Header */}
      <div className="bg-gradient-to-r from-blue-600 to-indigo-600 text-white p-6">
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-3">
            <Building2 className="h-8 w-8" />
            <div>
              <h2 className="text-2xl font-bold">Business Intelligence Summary</h2>
              <p className="text-blue-100">AI-powered insights for {business_data.store_name}</p>
            </div>
          </div>
          <div className="text-right text-sm text-blue-100">
            <div className="flex items-center space-x-1">
              <Clock className="h-4 w-4" />
              <span>Updated {formatDate(business_summary.generated_at)}</span>
            </div>
            <div className="mt-1">
              Powered by {business_summary.ai_provider === 'azure_cognitive_services' ? 'Azure AI' : 'AI Assistant'}
            </div>
          </div>
        </div>
      </div>

      {/* Key Metrics */}
      <div className="p-6 border-b border-gray-200">
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
          <div className="text-center">
            <div className="flex items-center justify-center w-12 h-12 bg-green-100 rounded-lg mx-auto mb-2">
              <DollarSign className="h-6 w-6 text-green-600" />
            </div>
            <div className="text-2xl font-bold text-gray-900">{formatCurrency(business_data.revenue_30d)}</div>
            <div className="text-sm text-gray-500">30-Day Revenue</div>
          </div>
          <div className="text-center">
            <div className="flex items-center justify-center w-12 h-12 bg-blue-100 rounded-lg mx-auto mb-2">
              <Users className="h-6 w-6 text-blue-600" />
            </div>
            <div className="text-2xl font-bold text-gray-900">{business_data.orders_30d}</div>
            <div className="text-sm text-gray-500">Orders</div>
          </div>
          <div className="text-center">
            <div className="flex items-center justify-center w-12 h-12 bg-purple-100 rounded-lg mx-auto mb-2">
              <Package className="h-6 w-6 text-purple-600" />
            </div>
            <div className="text-2xl font-bold text-gray-900">{business_data.total_products}</div>
            <div className="text-sm text-gray-500">Products</div>
          </div>
          <div className="text-center">
            <div className="flex items-center justify-center w-12 h-12 bg-orange-100 rounded-lg mx-auto mb-2">
              <TrendingUp className="h-6 w-6 text-orange-600" />
            </div>
            <div className="text-2xl font-bold text-gray-900">{formatCurrency(business_data.avg_order_value)}</div>
            <div className="text-sm text-gray-500">Avg Order Value</div>
          </div>
        </div>
      </div>

      {/* Executive Summary */}
      <div className="p-6">
        <div className="bg-white rounded-lg p-4 border-l-4 border-blue-500">
          <h3 className="text-lg font-semibold text-gray-900 mb-2">Executive Summary</h3>
          <p className="text-gray-700 leading-relaxed">{business_summary.executive_summary}</p>
        </div>
      </div>

      {/* Expandable Sections */}
      <div className="px-6 pb-6 space-y-4">
        {/* Key Insights */}
        <div className="bg-white rounded-lg border border-gray-200 overflow-hidden">
          <button
            onClick={() => toggleSection('insights')}
            className="w-full px-4 py-3 text-left bg-gray-50 hover:bg-gray-100 transition-colors flex items-center justify-between"
          >
            <div className="flex items-center space-x-2">
              <Lightbulb className="h-5 w-5 text-yellow-600" />
              <span className="font-medium text-gray-900">Key Insights</span>
              <span className="bg-yellow-100 text-yellow-800 text-xs px-2 py-1 rounded-full">
                {business_summary.key_insights.length}
              </span>
            </div>
            <div className={`transform transition-transform ${expandedSection === 'insights' ? 'rotate-180' : ''}`}>
              ▼
            </div>
          </button>
          {expandedSection === 'insights' && (
            <div className="p-4">
              <ul className="space-y-2">
                {business_summary.key_insights.map((insight, index) => (
                  <li key={index} className="flex items-start space-x-2">
                    <div className="w-2 h-2 bg-yellow-500 rounded-full mt-2 flex-shrink-0"></div>
                    <span className="text-gray-700">{insight}</span>
                  </li>
                ))}
              </ul>
            </div>
          )}
        </div>

        {/* Performance Highlights */}
        <div className="bg-white rounded-lg border border-gray-200 overflow-hidden">
          <button
            onClick={() => toggleSection('highlights')}
            className="w-full px-4 py-3 text-left bg-gray-50 hover:bg-gray-100 transition-colors flex items-center justify-between"
          >
            <div className="flex items-center space-x-2">
              <CheckCircle className="h-5 w-5 text-green-600" />
              <span className="font-medium text-gray-900">Performance Highlights</span>
              <span className="bg-green-100 text-green-800 text-xs px-2 py-1 rounded-full">
                {business_summary.performance_highlights.length}
              </span>
            </div>
            <div className={`transform transition-transform ${expandedSection === 'highlights' ? 'rotate-180' : ''}`}>
              ▼
            </div>
          </button>
          {expandedSection === 'highlights' && (
            <div className="p-4">
              <ul className="space-y-2">
                {business_summary.performance_highlights.map((highlight, index) => (
                  <li key={index} className="flex items-start space-x-2">
                    <CheckCircle className="w-4 h-4 text-green-500 mt-0.5 flex-shrink-0" />
                    <span className="text-gray-700">{highlight}</span>
                  </li>
                ))}
              </ul>
            </div>
          )}
        </div>

        {/* Strategic Recommendations */}
        <div className="bg-white rounded-lg border border-gray-200 overflow-hidden">
          <button
            onClick={() => toggleSection('recommendations')}
            className="w-full px-4 py-3 text-left bg-gray-50 hover:bg-gray-100 transition-colors flex items-center justify-between"
          >
            <div className="flex items-center space-x-2">
              <TrendingUp className="h-5 w-5 text-blue-600" />
              <span className="font-medium text-gray-900">Strategic Recommendations</span>
              <span className="bg-blue-100 text-blue-800 text-xs px-2 py-1 rounded-full">
                {business_summary.strategic_recommendations.length}
              </span>
            </div>
            <div className={`transform transition-transform ${expandedSection === 'recommendations' ? 'rotate-180' : ''}`}>
              ▼
            </div>
          </button>
          {expandedSection === 'recommendations' && (
            <div className="p-4">
              <ul className="space-y-3">
                {business_summary.strategic_recommendations.map((recommendation, index) => (
                  <li key={index} className="flex items-start space-x-3">
                    <div className="w-6 h-6 bg-blue-100 text-blue-600 rounded-full flex items-center justify-center text-sm font-medium flex-shrink-0">
                      {index + 1}
                    </div>
                    <span className="text-gray-700">{recommendation}</span>
                  </li>
                ))}
              </ul>
            </div>
          )}
        </div>

        {/* Priority Actions */}
        {business_summary.priority_actions.length > 0 && (
          <div className="bg-white rounded-lg border border-gray-200 overflow-hidden">
            <button
              onClick={() => toggleSection('actions')}
              className="w-full px-4 py-3 text-left bg-gray-50 hover:bg-gray-100 transition-colors flex items-center justify-between"
            >
              <div className="flex items-center space-x-2">
                <AlertCircle className="h-5 w-5 text-red-600" />
                <span className="font-medium text-gray-900">Priority Actions</span>
                <span className="bg-red-100 text-red-800 text-xs px-2 py-1 rounded-full">
                  {business_summary.priority_actions.length}
                </span>
              </div>
              <div className={`transform transition-transform ${expandedSection === 'actions' ? 'rotate-180' : ''}`}>
                ▼
              </div>
            </button>
            {expandedSection === 'actions' && (
              <div className="p-4">
                <ul className="space-y-2">
                  {business_summary.priority_actions.map((action, index) => (
                    <li key={index} className="flex items-start space-x-2">
                      <AlertCircle className="w-4 h-4 text-red-500 mt-0.5 flex-shrink-0" />
                      <span className="text-gray-700">{action}</span>
                    </li>
                  ))}
                </ul>
              </div>
            )}
          </div>
        )}
      </div>

      {/* Market Outlook */}
      {business_summary.market_outlook && (
        <div className="px-6 pb-6">
          <div className="bg-gradient-to-r from-indigo-50 to-purple-50 rounded-lg p-4 border border-indigo-200">
            <h3 className="text-lg font-semibold text-gray-900 mb-2 flex items-center space-x-2">
              <TrendingUp className="h-5 w-5 text-indigo-600" />
              <span>Market Outlook</span>
            </h3>
            <p className="text-gray-700 leading-relaxed">{business_summary.market_outlook}</p>
          </div>
        </div>
      )}
    </div>
  );
}