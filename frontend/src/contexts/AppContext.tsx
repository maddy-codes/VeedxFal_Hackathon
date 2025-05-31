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

  const getSampleAnalytics = (): DashboardAnalytics => {
    return {
      total_products: 156,
      active_products: 142,
      total_revenue: 45678.90,
      revenue_last_30d: 12345.67,
      revenue_change_percent: 15.2,
      avg_order_value: 89.45,
      total_orders: 512,
      orders_last_30d: 138,
      orders_change_percent: 8.7,
      top_selling_products: [],
      trending_products: [],
      pricing_opportunities: [],
      inventory_alerts: [],
      sync_status: 'completed',
    };
  };

  return {
    analytics: analytics || getSampleAnalytics(),
    setAnalytics,
    isLoading,
    setIsLoading,
  };
}