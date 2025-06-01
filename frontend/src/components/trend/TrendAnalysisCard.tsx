'use client';

import { useState } from 'react';
import { TrendSummary, TrendingProductData } from '@/types';
import { useTrendAnalysis, useTrendLabelStyle } from '@/hooks/useTrendAnalysis';
import { RefreshCw, TrendingUp, TrendingDown, Minus, AlertCircle } from 'lucide-react';

interface TrendAnalysisCardProps {
  shopId: number;
  className?: string;
}

export function TrendAnalysisCard({ shopId, className = '' }: TrendAnalysisCardProps) {
  const {
    trendSummary,
    trendingProducts,
    healthStatus,
    isLoading,
    error,
    fetchTrendSummary,
    fetchTrendingProducts,
    refreshTrendData,
    clearError
  } = useTrendAnalysis();

  const { getTrendLabelStyle, getTrendScoreColor } = useTrendLabelStyle();
  const [activeTab, setActiveTab] = useState<'summary' | 'trending'>('summary');

  // Load data on mount
  useState(() => {
    fetchTrendSummary(shopId);
    fetchTrendingProducts(shopId);
  });

  const handleRefresh = async () => {
    await refreshTrendData(shopId);
  };

  const renderTrendIcon = (label: string) => {
    switch (label) {
      case 'Hot':
        return <TrendingUp className="h-4 w-4 text-red-500" />;
      case 'Rising':
        return <TrendingUp className="h-4 w-4 text-orange-500" />;
      case 'Steady':
        return <Minus className="h-4 w-4 text-blue-500" />;
      case 'Declining':
        return <TrendingDown className="h-4 w-4 text-gray-500" />;
      default:
        return <Minus className="h-4 w-4 text-gray-500" />;
    }
  };

  const renderHealthStatus = () => {
    if (!healthStatus) return null;

    const isHealthy = healthStatus.status === 'healthy';
    const isDegraded = healthStatus.status === 'degraded';

    return (
      <div className="flex items-center space-x-2 text-sm">
        <div className={`w-2 h-2 rounded-full ${
          isHealthy ? 'bg-green-500' : isDegraded ? 'bg-yellow-500' : 'bg-red-500'
        }`} />
        <span className="text-gray-600">
          Service: {healthStatus.status}
        </span>
        {healthStatus.checks.database.response_time_ms && (
          <span className="text-gray-500">
            • DB: {healthStatus.checks.database.response_time_ms.toFixed(0)}ms
          </span>
        )}
      </div>
    );
  };

  const renderSummaryTab = () => {
    if (!trendSummary) {
      return (
        <div className="text-center py-8">
          <p className="text-gray-500">No trend summary available</p>
        </div>
      );
    }

    return (
      <div className="space-y-6">
        {/* Summary Stats */}
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
          {Object.entries(trendSummary.summary).map(([label, count]) => {
            const style = getTrendLabelStyle(label);
            const percentage = trendSummary.percentages?.[label as keyof typeof trendSummary.percentages] || 0;
            
            return (
              <div key={label} className="bg-gray-50 rounded-lg p-4">
                <div className="flex items-center justify-between mb-2">
                  <span className="text-sm font-medium text-gray-600">{label}</span>
                  {renderTrendIcon(label)}
                </div>
                <div className="text-2xl font-bold text-gray-900">{count}</div>
                <div className="text-sm text-gray-500">{percentage.toFixed(1)}%</div>
              </div>
            );
          })}
        </div>

        {/* Average Scores */}
        <div className="bg-gray-50 rounded-lg p-4">
          <h4 className="text-sm font-medium text-gray-900 mb-3">Average Scores</h4>
          <div className="grid grid-cols-3 gap-4">
            <div className="text-center">
              <div className="text-lg font-semibold text-gray-900">
                {trendSummary.average_scores?.google_trend_index?.toFixed(1) || '0.0'}
              </div>
              <div className="text-xs text-gray-500">Google Trends</div>
            </div>
            <div className="text-center">
              <div className="text-lg font-semibold text-gray-900">
                {trendSummary.average_scores?.social_score?.toFixed(1) || '0.0'}
              </div>
              <div className="text-xs text-gray-500">Social Score</div>
            </div>
            <div className="text-center">
              <div className={`text-lg font-semibold ${getTrendScoreColor(trendSummary.average_scores?.final_score || 0)}`}>
                {trendSummary.average_scores?.final_score?.toFixed(1) || '0.0'}
              </div>
              <div className="text-xs text-gray-500">Final Score</div>
            </div>
          </div>
        </div>

        {/* Last Updated */}
        {trendSummary.last_updated && (
          <div className="text-sm text-gray-500">
            Last updated: {new Date(trendSummary.last_updated).toLocaleString()}
          </div>
        )}
      </div>
    );
  };

  const renderTrendingTab = () => {
    if (!trendingProducts || trendingProducts.trending_products.length === 0) {
      return (
        <div className="text-center py-8">
          <p className="text-gray-500">No trending products available</p>
        </div>
      );
    }

    return (
      <div className="space-y-4">
        {trendingProducts.trending_products.map((product) => {
          const style = getTrendLabelStyle(product.trend_data.label);
          
          return (
            <div key={product.sku_code} className="border border-gray-200 rounded-lg p-4 hover:bg-gray-50">
              <div className="flex items-start justify-between">
                <div className="flex-1">
                  <div className="flex items-center space-x-3 mb-2">
                    <h5 className="font-medium text-gray-900">{product.product_title}</h5>
                    <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium border ${style.className}`}>
                      {style.icon} {product.trend_data.label}
                    </span>
                  </div>
                  <div className="text-sm text-gray-500 mb-2">
                    SKU: {product.sku_code} • ${product.current_price.toFixed(2)}
                  </div>
                  <div className="flex items-center space-x-4 text-sm">
                    <span className="text-gray-600">
                      Google: {product.trend_data.google_trend_index}
                    </span>
                    <span className="text-gray-600">
                      Social: {product.trend_data.social_score}
                    </span>
                    <span className={`font-medium ${getTrendScoreColor(product.trend_data.final_score)}`}>
                      Final: {product.trend_data.final_score}
                    </span>
                  </div>
                </div>
                {product.image_url && (
                  <div className="flex-shrink-0 ml-4">
                    <img
                      src={product.image_url}
                      alt={product.product_title}
                      className="w-12 h-12 rounded-lg object-cover"
                    />
                  </div>
                )}
              </div>
            </div>
          );
        })}
      </div>
    );
  };

  return (
    <div className={`bg-white rounded-lg shadow-lg ${className}`}>
      {/* Header */}
      <div className="px-6 py-4 border-b border-gray-200">
        <div className="flex items-center justify-between">
          <div>
            <h3 className="text-lg font-medium text-gray-900">Trend Analysis</h3>
            {renderHealthStatus()}
          </div>
          <button
            onClick={handleRefresh}
            disabled={isLoading}
            className="inline-flex items-center px-3 py-2 border border-gray-300 shadow-sm text-sm leading-4 font-medium rounded-md text-gray-700 bg-white hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary disabled:opacity-50"
          >
            <RefreshCw className={`h-4 w-4 mr-2 ${isLoading ? 'animate-spin' : ''}`} />
            Refresh
          </button>
        </div>
      </div>

      {/* Error Display */}
      {error && (
        <div className="px-6 py-4 bg-red-50 border-b border-red-200">
          <div className="flex items-center">
            <AlertCircle className="h-5 w-5 text-red-400 mr-2" />
            <span className="text-sm text-red-700">{error}</span>
            <button
              onClick={clearError}
              className="ml-auto text-red-400 hover:text-red-600"
            >
              ×
            </button>
          </div>
        </div>
      )}

      {/* Tabs */}
      <div className="px-6 py-4 border-b border-gray-200">
        <div className="flex space-x-4">
          <button
            onClick={() => setActiveTab('summary')}
            className={`px-3 py-2 text-sm font-medium rounded-md transition-colors ${
              activeTab === 'summary'
                ? 'bg-primary text-white'
                : 'text-gray-600 hover:text-primary hover:bg-gray-100'
            }`}
          >
            Summary
          </button>
          <button
            onClick={() => setActiveTab('trending')}
            className={`px-3 py-2 text-sm font-medium rounded-md transition-colors ${
              activeTab === 'trending'
                ? 'bg-primary text-white'
                : 'text-gray-600 hover:text-primary hover:bg-gray-100'
            }`}
          >
            Trending Products
          </button>
        </div>
      </div>

      {/* Content */}
      <div className="px-6 py-6">
        {isLoading && !trendSummary && !trendingProducts ? (
          <div className="text-center py-8">
            <RefreshCw className="h-8 w-8 animate-spin mx-auto text-gray-400 mb-2" />
            <p className="text-gray-500">Loading trend analysis...</p>
          </div>
        ) : (
          <>
            {activeTab === 'summary' && renderSummaryTab()}
            {activeTab === 'trending' && renderTrendingTab()}
          </>
        )}
      </div>
    </div>
  );
}