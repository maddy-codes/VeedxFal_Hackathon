'use client';

import React, { useState, useEffect } from 'react';
import { useAuth } from '@/contexts/AuthContext';
import AIBusinessManager from '@/components/avatar/AIBusinessManager';
import { BusinessContextCard } from '@/components/business/BusinessContextCard';
import { TrendAnalysisCard } from '@/components/trend/TrendAnalysisCard';
import { TrendBadge } from '@/components/trend/TrendBadge';
import { useTrendAnalysis } from '@/hooks/useTrendAnalysis';
import { TrendSummary, TrendingProductData } from '@/types';
import { TrendingUp, TrendingDown, BarChart3, Package, RefreshCw, MessageCircle, Activity, Brain } from 'lucide-react';

const InsightsPage: React.FC = () => {
  const { store } = useAuth();
  const [activeTab, setActiveTab] = useState('overview');
  
  const {
    trendSummary,
    trendingProducts,
    isLoading: isTrendLoading,
    error: trendError,
    fetchTrendSummary,
    fetchTrendingProducts,
    refreshTrendData
  } = useTrendAnalysis();

  const tabs = [
    { id: 'overview', name: 'Overview', icon: Activity },
    { id: 'ai-manager', name: 'AI Business Manager', icon: MessageCircle },
    { id: 'analysis', name: 'Trend Analysis', icon: Brain },
  ];

  useEffect(() => {
    if (store?.id) {
      fetchTrendSummary(store.id);
      fetchTrendingProducts(store.id);
    }
  }, [store?.id]);

  const handleRefreshAll = async () => {
    if (store?.id) {
      await refreshTrendData(store.id);
    }
  };

  if (!store) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="text-center">
          <h2 className="text-xl font-semibold text-gray-900 mb-2">No Store Connected</h2>
          <p className="text-gray-600">Please connect your store to view insights.</p>
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Tab Navigation */}
      <div className="border-b border-gray-200">
        <nav className="-mb-px flex space-x-8">
          {tabs.map((tab) => {
            const Icon = tab.icon;
            return (
              <button
                key={tab.id}
                onClick={() => setActiveTab(tab.id)}
                className={`
                  flex items-center py-4 px-1 border-b-2 font-medium text-sm transition-colors
                  ${activeTab === tab.id
                    ? 'border-blue-500 text-blue-600'
                    : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                  }
                `}
              >
                <Icon className="w-5 h-5 mr-2" />
                {tab.name}
              </button>
            );
          })}
        </nav>
      </div>

      {/* Tab Content */}
      <div className="space-y-6">
        {activeTab === 'overview' && (
          <div className="space-y-6">
            {/* Refresh Button */}
            <div className="flex justify-end">
              <button
                onClick={handleRefreshAll}
                disabled={isTrendLoading}
                className="flex items-center space-x-2 bg-blue-600 text-white px-4 py-2 rounded-md hover:bg-blue-700 disabled:opacity-50 transition-colors"
              >
                <RefreshCw className={`h-4 w-4 ${isTrendLoading ? 'animate-spin' : ''}`} />
                <span>Refresh All</span>
              </button>
            </div>
            {/* Business Context */}
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-6">
              <div className="lg:col-span-2">
                <BusinessContextCard shopId={store.id} />
              </div>
            </div>

        {/* Trend Summary Cards */}
        {trendSummary && (
          <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-6">
            <div className="bg-white rounded-lg shadow-md p-6">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm font-medium text-gray-600">Hot Products</p>
                  <p className="text-2xl font-bold text-red-600">{trendSummary.summary.Hot}</p>
                  <p className="text-xs text-gray-500">{trendSummary.percentages.Hot.toFixed(1)}% of total</p>
                </div>
                <TrendingUp className="h-8 w-8 text-red-500" />
              </div>
            </div>

            <div className="bg-white rounded-lg shadow-md p-6">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm font-medium text-gray-600">Rising Products</p>
                  <p className="text-2xl font-bold text-orange-600">{trendSummary.summary.Rising}</p>
                  <p className="text-xs text-gray-500">{trendSummary.percentages.Rising.toFixed(1)}% of total</p>
                </div>
                <TrendingUp className="h-8 w-8 text-orange-500" />
              </div>
            </div>

            <div className="bg-white rounded-lg shadow-md p-6">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm font-medium text-gray-600">Steady Products</p>
                  <p className="text-2xl font-bold text-blue-600">{trendSummary.summary.Steady}</p>
                  <p className="text-xs text-gray-500">{trendSummary.percentages.Steady.toFixed(1)}% of total</p>
                </div>
                <BarChart3 className="h-8 w-8 text-blue-500" />
              </div>
            </div>

            <div className="bg-white rounded-lg shadow-md p-6">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm font-medium text-gray-600">Declining Products</p>
                  <p className="text-2xl font-bold text-gray-600">{trendSummary.summary.Declining}</p>
                  <p className="text-xs text-gray-500">{trendSummary.percentages.Declining.toFixed(1)}% of total</p>
                </div>
                <TrendingDown className="h-8 w-8 text-gray-500" />
              </div>
            </div>
          </div>
        )}

        {/* Trend Analysis and Trending Products */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-6">
          {/* Trend Analysis Card */}
          <div className="lg:col-span-1">
            <TrendAnalysisCard shopId={store.id} />
          </div>

          {/* Trending Products */}
          <div className="lg:col-span-1">
            <div className="bg-white rounded-lg shadow-md p-6">
              <div className="flex items-center justify-between mb-4">
                <h3 className="text-lg font-semibold text-gray-900">Trending Products</h3>
                <Package className="h-5 w-5 text-gray-400" />
              </div>
              
              {isTrendLoading ? (
                <div className="space-y-3">
                  {[...Array(3)].map((_, i) => (
                    <div key={i} className="animate-pulse">
                      <div className="h-4 bg-gray-200 rounded w-3/4 mb-2"></div>
                      <div className="h-3 bg-gray-200 rounded w-1/2"></div>
                    </div>
                  ))}
                </div>
              ) : trendingProducts && trendingProducts.trending_products.length > 0 ? (
                <div className="space-y-3">
                  {trendingProducts.trending_products.slice(0, 5).map((product: TrendingProductData, index: number) => (
                    <div key={index} className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
                      <div className="flex-1">
                        <p className="text-sm font-medium text-gray-900 truncate">
                          {product.product_title}
                        </p>
                        <div className="flex items-center space-x-2 mt-1">
                          <TrendBadge label={product.trend_data.label} />
                          <span className="text-xs text-gray-500">
                            Score: {product.trend_data.final_score.toFixed(1)}
                          </span>
                        </div>
                      </div>
                      <div className="text-right">
                        <p className="text-sm font-semibold text-gray-900">
                          ${product.current_price.toFixed(2)}
                        </p>
                      </div>
                    </div>
                  ))}
                </div>
              ) : (
                <div className="text-center py-8">
                  <Package className="h-12 w-12 text-gray-300 mx-auto mb-4" />
                  <p className="text-gray-500">No trending products data available</p>
                </div>
              )}
            </div>
          </div>
        </div>


        {/* Average Trend Scores */}
        {trendSummary && (
          <div className="bg-white rounded-lg shadow-md p-6 mb-6">
            <h3 className="text-lg font-semibold text-gray-900 mb-4">Average Trend Scores</h3>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              <div className="text-center">
                <div className="text-2xl font-bold text-blue-600">
                  {trendSummary.average_scores.google_trend_index.toFixed(1)}
                </div>
                <div className="text-sm text-gray-600">Google Trends Index</div>
                <div className="w-full bg-gray-200 rounded-full h-2 mt-2">
                  <div 
                    className="bg-blue-600 h-2 rounded-full" 
                    style={{ width: `${trendSummary.average_scores.google_trend_index}%` }}
                  ></div>
                </div>
              </div>
              
              <div className="text-center">
                <div className="text-2xl font-bold text-purple-600">
                  {trendSummary.average_scores.social_score.toFixed(1)}
                </div>
                <div className="text-sm text-gray-600">Social Score</div>
                <div className="w-full bg-gray-200 rounded-full h-2 mt-2">
                  <div 
                    className="bg-purple-600 h-2 rounded-full" 
                    style={{ width: `${trendSummary.average_scores.social_score}%` }}
                  ></div>
                </div>
              </div>
              
              <div className="text-center">
                <div className="text-2xl font-bold text-green-600">
                  {trendSummary.average_scores.final_score.toFixed(1)}
                </div>
                <div className="text-sm text-gray-600">Overall Trend Score</div>
                <div className="w-full bg-gray-200 rounded-full h-2 mt-2">
                  <div 
                    className="bg-green-600 h-2 rounded-full" 
                    style={{ width: `${trendSummary.average_scores.final_score}%` }}
                  ></div>
                </div>
              </div>
            </div>
          </div>
        )}

            {/* AI Manager CTA */}
            <div className="bg-gradient-to-r from-blue-50 to-purple-50 border border-blue-200 rounded-lg p-6">
              <div className="flex items-center justify-between">
                <div>
                  <h3 className="text-lg font-semibold text-gray-900 mb-2">
                    🎬 Ready for Your Business Briefing?
                  </h3>
                  <p className="text-gray-700 mb-4">
                    Get personalized video insights from Jaz, your AI business manager.
                    Discover key performance metrics, trends, and strategic recommendations.
                  </p>
                </div>
                <button
                  onClick={() => setActiveTab('ai-manager')}
                  className="flex items-center px-6 py-3 bg-gradient-to-r from-blue-600 to-purple-600 text-white font-semibold rounded-lg hover:from-blue-700 hover:to-purple-700 transition-all duration-200 shadow-lg hover:shadow-xl"
                >
                  <MessageCircle className="w-5 h-5 mr-2" />
                  Speak with Jaz
                </button>
              </div>
            </div>
          </div>
        )}

        {activeTab === 'ai-manager' && (
          <div className="space-y-6">
            <AIBusinessManager shopId={store.id} />
          </div>
        )}

        {activeTab === 'analysis' && (
          <div className="space-y-6">
            <TrendAnalysisCard shopId={store.id} />
          </div>
        )}
      </div>
    </div>
  );
};

export default InsightsPage;