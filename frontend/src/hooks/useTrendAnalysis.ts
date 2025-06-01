'use client';

import { useState, useCallback, useEffect } from 'react';
import { apiClient } from '@/lib/api';
import {
  TrendSummary,
  TrendingProductsResponse,
  TrendAnalysisResponse,
  TrendHealthCheck,
  TrendAnalysisRequest,
  BatchAnalysisResponse,
  TrendUpdate
} from '@/types';

export interface UseTrendAnalysisReturn {
  // State
  trendSummary: TrendSummary | null;
  trendingProducts: TrendingProductsResponse | null;
  trendInsights: TrendAnalysisResponse | null;
  healthStatus: TrendHealthCheck | null;
  isLoading: boolean;
  error: string | null;

  // Actions
  fetchTrendSummary: (shopId: number) => Promise<void>;
  fetchTrendingProducts: (shopId: number, label?: string, limit?: number) => Promise<void>;
  fetchTrendInsights: (shopId: number, skuCode?: string, maxAgeHours?: number) => Promise<void>;
  analyzeProductTrend: (shopId: number, request: TrendAnalysisRequest) => Promise<TrendUpdate | null>;
  analyzeTrendsBatch: (shopId: number, products: TrendAnalysisRequest[]) => Promise<BatchAnalysisResponse | null>;
  refreshTrendData: (shopId: number, skuCodes?: string[]) => Promise<void>;
  checkHealth: () => Promise<void>;
  clearError: () => void;
}

export function useTrendAnalysis(): UseTrendAnalysisReturn {
  const [trendSummary, setTrendSummary] = useState<TrendSummary | null>(null);
  const [trendingProducts, setTrendingProducts] = useState<TrendingProductsResponse | null>(null);
  const [trendInsights, setTrendInsights] = useState<TrendAnalysisResponse | null>(null);
  const [healthStatus, setHealthStatus] = useState<TrendHealthCheck | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const clearError = useCallback(() => {
    setError(null);
  }, []);

  const handleError = useCallback((err: any) => {
    const errorMessage = err?.message || err?.detail || 'An unexpected error occurred';
    setError(errorMessage);
    console.error('Trend Analysis Error:', err);
  }, []);

  const fetchTrendSummary = useCallback(async (shopId: number) => {
    try {
      setIsLoading(true);
      setError(null);
      const data = await apiClient.getTrendSummary(shopId);
      setTrendSummary(data);
    } catch (err) {
      handleError(err);
    } finally {
      setIsLoading(false);
    }
  }, [handleError]);

  const fetchTrendingProducts = useCallback(async (
    shopId: number, 
    label?: string, 
    limit: number = 10
  ) => {
    try {
      setIsLoading(true);
      setError(null);
      const data = await apiClient.getTrendingProducts(shopId, { label, limit });
      setTrendingProducts(data);
    } catch (err) {
      handleError(err);
    } finally {
      setIsLoading(false);
    }
  }, [handleError]);

  const fetchTrendInsights = useCallback(async (
    shopId: number,
    skuCode?: string,
    maxAgeHours: number = 24
  ) => {
    try {
      setIsLoading(true);
      setError(null);
      const data = await apiClient.getTrendInsights(shopId, { sku_code: skuCode, max_age_hours: maxAgeHours });
      setTrendInsights(data);
    } catch (err) {
      handleError(err);
    } finally {
      setIsLoading(false);
    }
  }, [handleError]);

  const analyzeProductTrend = useCallback(async (
    shopId: number,
    request: TrendAnalysisRequest
  ): Promise<TrendUpdate | null> => {
    try {
      setIsLoading(true);
      setError(null);
      const data = await apiClient.analyzeProductTrend(shopId, request);
      return data;
    } catch (err) {
      handleError(err);
      return null;
    } finally {
      setIsLoading(false);
    }
  }, [handleError]);

  const analyzeTrendsBatch = useCallback(async (
    shopId: number,
    products: TrendAnalysisRequest[]
  ): Promise<BatchAnalysisResponse | null> => {
    try {
      setIsLoading(true);
      setError(null);
      const data = await apiClient.analyzeTrendsBatch(shopId, products);
      return data;
    } catch (err) {
      handleError(err);
      return null;
    } finally {
      setIsLoading(false);
    }
  }, [handleError]);

  const refreshTrendData = useCallback(async (shopId: number, skuCodes?: string[]) => {
    try {
      setIsLoading(true);
      setError(null);
      await apiClient.refreshTrendData(shopId, skuCodes);
      // Optionally refresh the current data
      if (trendSummary) {
        await fetchTrendSummary(shopId);
      }
      if (trendingProducts) {
        await fetchTrendingProducts(shopId);
      }
    } catch (err) {
      handleError(err);
    } finally {
      setIsLoading(false);
    }
  }, [handleError, trendSummary, trendingProducts, fetchTrendSummary, fetchTrendingProducts]);

  const checkHealth = useCallback(async () => {
    try {
      setError(null);
      const data = await apiClient.getTrendAnalysisHealth();
      setHealthStatus(data);
    } catch (err) {
      handleError(err);
    }
  }, [handleError]);

  // Auto-check health on mount
  useEffect(() => {
    checkHealth();
  }, [checkHealth]);

  return {
    // State
    trendSummary,
    trendingProducts,
    trendInsights,
    healthStatus,
    isLoading,
    error,

    // Actions
    fetchTrendSummary,
    fetchTrendingProducts,
    fetchTrendInsights,
    analyzeProductTrend,
    analyzeTrendsBatch,
    refreshTrendData,
    checkHealth,
    clearError,
  };
}

// Hook for getting trend label styling
export function useTrendLabelStyle() {
  const getTrendLabelStyle = useCallback((label: string) => {
    switch (label) {
      case 'Hot':
        return {
          className: 'bg-red-100 text-red-800 border-red-200',
          icon: '🔥',
          color: 'red'
        };
      case 'Rising':
        return {
          className: 'bg-orange-100 text-orange-800 border-orange-200',
          icon: '📈',
          color: 'orange'
        };
      case 'Steady':
        return {
          className: 'bg-blue-100 text-blue-800 border-blue-200',
          icon: '➡️',
          color: 'blue'
        };
      case 'Declining':
        return {
          className: 'bg-gray-100 text-gray-800 border-gray-200',
          icon: '📉',
          color: 'gray'
        };
      default:
        return {
          className: 'bg-gray-100 text-gray-800 border-gray-200',
          icon: '❓',
          color: 'gray'
        };
    }
  }, []);

  const getTrendScoreColor = useCallback((score: number) => {
    if (score >= 80) return 'text-red-600';
    if (score >= 60) return 'text-orange-600';
    if (score >= 40) return 'text-blue-600';
    return 'text-gray-600';
  }, []);

  return {
    getTrendLabelStyle,
    getTrendScoreColor,
  };
}