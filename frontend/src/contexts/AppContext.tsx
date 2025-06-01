'use client';

import React, { createContext, useContext, useReducer, ReactNode, useCallback } from 'react';
import { 
  ProductDetail, 
  DashboardAnalytics, 
  BusinessInsight, 
  ProductFilter,
  AppContextType 
} from '@/types';

// App state type
interface AppState {
  selectedFilter: ProductFilter;
  products: ProductDetail[];
  analytics: DashboardAnalytics | null;
  insights: BusinessInsight[];
  isLoading: boolean;
  error: string | null;
}

// App actions
type AppAction =
  | { type: 'SET_FILTER'; payload: ProductFilter }
  | { type: 'SET_PRODUCTS'; payload: ProductDetail[] }
  | { type: 'SET_ANALYTICS'; payload: DashboardAnalytics }
  | { type: 'SET_INSIGHTS'; payload: BusinessInsight[] }
  | { type: 'SET_LOADING'; payload: boolean }
  | { type: 'SET_ERROR'; payload: string | null }
  | { type: 'CLEAR_ERROR' }
  | { type: 'RESET_STATE' };

// Initial state
const initialState: AppState = {
  selectedFilter: 'All',
  products: [],
  analytics: null,
  insights: [],
  isLoading: false,
  error: null,
};

// App reducer
function appReducer(state: AppState, action: AppAction): AppState {
  switch (action.type) {
    case 'SET_FILTER':
      return {
        ...state,
        selectedFilter: action.payload,
      };
    case 'SET_PRODUCTS':
      return {
        ...state,
        products: action.payload,
        error: null,
      };
    case 'SET_ANALYTICS':
      return {
        ...state,
        analytics: action.payload,
        error: null,
      };
    case 'SET_INSIGHTS':
      return {
        ...state,
        insights: action.payload,
        error: null,
      };
    case 'SET_LOADING':
      return {
        ...state,
        isLoading: action.payload,
      };
    case 'SET_ERROR':
      return {
        ...state,
        error: action.payload,
        isLoading: false,
      };
    case 'CLEAR_ERROR':
      return {
        ...state,
        error: null,
      };
    case 'RESET_STATE':
      return initialState;
    default:
      return state;
  }
}

// Create context
const AppContext = createContext<AppContextType | undefined>(undefined);

// App provider component
interface AppProviderProps {
  children: ReactNode;
}

export function AppProvider({ children }: AppProviderProps) {
  const [state, dispatch] = useReducer(appReducer, initialState);

  // Filter products based on selected filter
  const getFilteredProducts = (): ProductDetail[] => {
    if (state.selectedFilter === 'All') {
      return state.products;
    }

    return state.products.filter(product => {
      switch (state.selectedFilter) {
        case 'Underpriced':
          return product.recommendation_type === 'underpriced';
        case 'Overstocked':
          return product.inventory_level > 50; // Assuming >50 is overstocked
        case 'Hot':
          return product.trend_label === 'Hot' || product.trend_label === 'Rising';
        default:
          return true;
      }
    });
  };

  // Get sample data for mockup implementation
  const getSampleProducts = (): ProductDetail[] => {
    return [
      {
        sku_id: 1,
        shop_id: 1,
        sku_code: 'WE001',
        product_title: 'Wireless Earbuds',
        current_price: 49.99,
        inventory_level: 25,
        cost_price: 30.00,
        status: 'active',
        created_at: new Date().toISOString(),
        updated_at: new Date().toISOString(),
        recommended_price: 59.99,
        recommendation_type: 'underpriced',
        pricing_reason: 'Market analysis shows potential for price increase',
        confidence_score: 0.85,
        trend_label: 'Stable',
      },
      {
        sku_id: 2,
        shop_id: 1,
        sku_code: 'CS001',
        product_title: 'Classic Sneaker',
        current_price: 89.99,
        inventory_level: 75,
        cost_price: 45.00,
        status: 'active',
        created_at: new Date().toISOString(),
        updated_at: new Date().toISOString(),
        recommendation_type: 'overstocked',
        pricing_reason: 'High inventory levels suggest clearance sale',
        confidence_score: 0.75,
        trend_label: 'Declining',
      },
      {
        sku_id: 3,
        shop_id: 1,
        sku_code: 'DJ001',
        product_title: 'Denim Jacket',
        current_price: 79.99,
        inventory_level: 15,
        cost_price: 40.00,
        status: 'active',
        created_at: new Date().toISOString(),
        updated_at: new Date().toISOString(),
        trend_label: 'Hot',
        trend_score: 85,
        pricing_reason: 'Trending upward in market demand',
        confidence_score: 0.90,
      },
      {
        sku_id: 4,
        shop_id: 1,
        sku_code: 'SW001',
        product_title: 'Smartwatch',
        current_price: 199.99,
        inventory_level: 8,
        cost_price: 120.00,
        status: 'active',
        created_at: new Date().toISOString(),
        updated_at: new Date().toISOString(),
        trend_label: 'Hot',
        trend_score: 92,
        pricing_reason: 'High demand currently',
        confidence_score: 0.95,
      },
    ];
  };

  // Memoize functions to prevent unnecessary re-renders
  const setSelectedFilter = useCallback((filter: ProductFilter) => {
    dispatch({ type: 'SET_FILTER', payload: filter });
  }, []);

  const setProducts = useCallback((products: ProductDetail[]) => {
    dispatch({ type: 'SET_PRODUCTS', payload: products });
  }, []);

  const setAnalytics = useCallback((analytics: DashboardAnalytics) => {
    dispatch({ type: 'SET_ANALYTICS', payload: analytics });
  }, []);

  const setInsights = useCallback((insights: BusinessInsight[]) => {
    dispatch({ type: 'SET_INSIGHTS', payload: insights });
  }, []);

  const setIsLoading = useCallback((loading: boolean) => {
    dispatch({ type: 'SET_LOADING', payload: loading });
  }, []);

  const contextValue: AppContextType = {
    selectedFilter: state.selectedFilter,
    setSelectedFilter,
    products: getFilteredProducts(),
    setProducts,
    analytics: state.analytics,
    setAnalytics,
    insights: state.insights,
    setInsights,
    isLoading: state.isLoading,
    setIsLoading,
  };

  return (
    <AppContext.Provider value={contextValue}>
      {children}
    </AppContext.Provider>
  );
}

// Custom hook to use app context
export function useApp(): AppContextType {
  const context = useContext(AppContext);
  if (context === undefined) {
    throw new Error('useApp must be used within an AppProvider');
  }
  return context;
}

// Hook for product filtering
export function useProductFilter() {
  const { selectedFilter, setSelectedFilter, products } = useApp();

  const filterOptions: ProductFilter[] = ['All', 'Underpriced', 'Overstocked', 'Hot'];

  const getFilterCount = (filter: ProductFilter): number => {
    if (filter === 'All') return products.length;
    
    // This would normally come from the full product list, not filtered
    return products.filter(product => {
      switch (filter) {
        case 'Underpriced':
          return product.recommendation_type === 'underpriced';
        case 'Overstocked':
          return product.inventory_level > 50;
        case 'Hot':
          return product.trend_label === 'Hot' || product.trend_label === 'Rising';
        default:
          return true;
      }
    }).length;
  };

  return {
    selectedFilter,
    setSelectedFilter,
    filterOptions,
    getFilterCount,
  };
}

// Hook for analytics data
export function useAnalytics() {
  const { analytics, setAnalytics, isLoading, setIsLoading } = useApp();

  // Fetch real analytics data from backend
  const fetchAnalytics = useCallback(async () => {
    try {
      setIsLoading(true);
      
      // For now, use shop_id=4 (the one with data)
      const response = await fetch('/api/v1/analytics/dashboard?shop_id=4', {
        method: 'GET',
        headers: {
          'Content-Type': 'application/json',
          // Add auth header when available
          // 'Authorization': `Bearer ${token}`,
        },
      });

      if (response.ok) {
        const data = await response.json();
        setAnalytics(data);
      } else {
        console.warn('Failed to fetch analytics, using sample data');
        setAnalytics(getSampleAnalytics());
      }
    } catch (error) {
      console.warn('Error fetching analytics, using sample data:', error);
      setAnalytics(getSampleAnalytics());
    } finally {
      setIsLoading(false);
    }
  }, [setAnalytics, setIsLoading]);

  const getSampleAnalytics = (): DashboardAnalytics => {
    return {
      total_products: 172,
      active_products: 170,
      total_revenue: 290614.07,
      revenue_last_30d: 290614.07,
      revenue_change_percent: 15.2,
      avg_order_value: 231.01,
      total_orders: 429,
      orders_last_30d: 429,
      orders_change_percent: 8.7,
      top_selling_products: [
        {
          sku_code: 'sku-hosted-1',
          product_title: 'Top Selling Product',
          total_revenue: 27347.12,
          total_quantity: 12,
          avg_price: 2278.93,
          image_url: undefined,
        }
      ],
      trending_products: [
        {
          sku_code: 'VN-09-7-beige',
          product_title: 'Trending Product',
          trend_label: 'Hot',
          trend_score: 85,
          google_trend_index: 90,
          social_score: 80,
          current_price: 89.99,
          image_url: undefined,
        }
      ],
      pricing_opportunities: [],
      inventory_alerts: [
        {
          sku_code: 'AsTi-01-8-black',
          product_title: 'Low Stock Product',
          current_inventory: 3,
          alert_type: 'low_stock',
          severity: 'warning',
          message: 'Only 3 units left',
          recommended_action: 'Consider restocking soon',
        }
      ],
      sync_status: 'completed',
    };
  };

  // Auto-fetch analytics on mount
  React.useEffect(() => {
    if (!analytics) {
      fetchAnalytics();
    }
  }, [analytics, fetchAnalytics]);

  return {
    analytics: analytics || getSampleAnalytics(),
    setAnalytics,
    isLoading,
    setIsLoading,
    fetchAnalytics,
  };
}

// Hook for time-series data
export function useTimeSeriesData(days: number = 30) {
  const [timeSeriesData, setTimeSeriesData] = React.useState<Array<{
    date: string;
    daily_revenue: number;
    daily_orders: number;
    daily_quantity: number;
  }>>([]);
  const [isLoading, setIsLoading] = React.useState(false);

  const fetchTimeSeriesData = useCallback(async () => {
    try {
      setIsLoading(true);
      
      // For now, use shop_id=4 (the one with data)
      const response = await fetch(`/api/v1/analytics/time-series?shop_id=4&days=${days}`, {
        method: 'GET',
        headers: {
          'Content-Type': 'application/json',
          // Add auth header when available
          // 'Authorization': `Bearer ${token}`,
        },
      });

      if (response.ok) {
        const data = await response.json();
        setTimeSeriesData(data);
      } else {
        console.warn('Failed to fetch time-series data, using sample data');
        setTimeSeriesData(getSampleTimeSeriesData(days));
      }
    } catch (error) {
      console.warn('Error fetching time-series data, using sample data:', error);
      setTimeSeriesData(getSampleTimeSeriesData(days));
    } finally {
      setIsLoading(false);
    }
  }, [days]);

  const getSampleTimeSeriesData = (days: number) => {
    const data = [];
    const today = new Date();
    
    for (let i = days - 1; i >= 0; i--) {
      const date = new Date(today);
      date.setDate(date.getDate() - i);
      
      // Generate realistic sample data with some variation
      const baseRevenue = 8000 + Math.random() * 4000;
      const baseOrders = 15 + Math.random() * 10;
      
      data.push({
        date: date.toISOString().split('T')[0],
        daily_revenue: Math.round(baseRevenue * 100) / 100,
        daily_orders: Math.round(baseOrders),
        daily_quantity: Math.round(baseOrders * (1 + Math.random() * 2)),
      });
    }
    
    return data;
  };

  // Auto-fetch time-series data on mount or when days change
  React.useEffect(() => {
    fetchTimeSeriesData();
  }, [fetchTimeSeriesData]);

  return {
    timeSeriesData,
    isLoading,
    fetchTimeSeriesData,
  };
}