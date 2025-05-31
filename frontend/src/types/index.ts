// Authentication types
export interface User {
  id: string;
  email: string;
  user_metadata?: Record<string, any>;
  app_metadata?: Record<string, any>;
}

export interface LoginRequest {
  email: string;
  password: string;
}

export interface LoginResponse {
  access_token: string;
  token_type: string;
  expires_in: number;
  user: User;
}

export interface Store {
  id: number;
  shop_domain: string;
  shop_name: string;
  is_active: boolean;
  shop_config: Record<string, any>;
  created_at: string;
  updated_at: string;
}

// Product types
export interface Product {
  sku_id: number;
  shop_id: number;
  shopify_product_id?: number;
  sku_code: string;
  product_title: string;
  variant_title?: string;
  current_price: number;
  inventory_level: number;
  cost_price?: number;
  image_url?: string;
  status: string;
  created_at: string;
  updated_at: string;
}

export interface ProductDetail extends Product {
  competitor_min_price?: number;
  competitor_max_price?: number;
  competitor_count?: number;
  google_trend_index?: number;
  social_score?: number;
  trend_score?: number;
  trend_label?: string;
  recommended_price?: number;
  pricing_reason?: string;
  recommendation_type?: string;
  confidence_score?: number;
  current_margin_percent?: number;
  recommended_margin_percent?: number;
}

export interface ProductListResponse {
  products: ProductDetail[];
  total: number;
  page: number;
  limit: number;
  has_next: boolean;
}

// Analytics types
export interface TopProduct {
  sku_code: string;
  product_title: string;
  total_revenue: number;
  total_quantity: number;
  avg_price: number;
  image_url?: string;
}

export interface TrendingProduct {
  sku_code: string;
  product_title: string;
  trend_label: string;
  trend_score: number;
  google_trend_index?: number;
  social_score?: number;
  current_price: number;
  image_url?: string;
}

export interface PricingOpportunity {
  sku_code: string;
  product_title: string;
  current_price: number;
  recommended_price: number;
  price_difference: number;
  price_change_percent: number;
  recommendation_type: string;
  confidence_score: number;
  reasoning: string;
}

export interface InventoryAlert {
  sku_code: string;
  product_title: string;
  current_inventory: number;
  alert_type: string;
  severity: string;
  message: string;
  recommended_action: string;
}

export interface DashboardAnalytics {
  total_products: number;
  active_products: number;
  total_revenue: number;
  revenue_last_30d: number;
  revenue_change_percent?: number;
  avg_order_value: number;
  total_orders: number;
  orders_last_30d: number;
  orders_change_percent?: number;
  top_selling_products: TopProduct[];
  trending_products: TrendingProduct[];
  pricing_opportunities: PricingOpportunity[];
  inventory_alerts: InventoryAlert[];
  last_sync_at?: string;
  sync_status: string;
}

export interface BusinessInsight {
  insight_type: string;
  title: string;
  description: string;
  impact_level: string;
  priority: number;
  data: Record<string, any>;
  recommendation: string;
  potential_value?: number;
}

export interface InsightsResponse {
  insights: BusinessInsight[];
  generated_at: string;
}

// Form types
export interface SignUpFormData {
  name: string;
  email: string;
  password: string;
}

export interface LoginFormData {
  email: string;
  password: string;
}

export interface PricingCalculatorData {
  costPrice: number;
  markupPercentage: number;
}

// Filter types
export type ProductFilter = "All" | "Underpriced" | "Overstocked" | "Hot";

// API Response types
export interface ApiResponse<T> {
  data?: T;
  error?: string;
  message?: string;
}

// Context types
export interface AuthContextType {
  user: User | null;
  store: Store | null;
  isLoading: boolean;
  login: (email: string, password: string) => Promise<void>;
  logout: () => Promise<void>;
  refreshToken: () => Promise<void>;
}

export interface AppContextType {
  selectedFilter: ProductFilter;
  setSelectedFilter: (filter: ProductFilter) => void;
  products: ProductDetail[];
  setProducts: (products: ProductDetail[]) => void;
  analytics: DashboardAnalytics | null;
  setAnalytics: (analytics: DashboardAnalytics) => void;
  insights: BusinessInsight[];
  setInsights: (insights: BusinessInsight[]) => void;
  isLoading: boolean;
  setIsLoading: (loading: boolean) => void;
}

// Video types
export interface VideoData {
  id: string;
  title: string;
  url: string;
  thumbnail?: string;
  duration?: number;
  created_at: string;
}

// Upload types
export interface UploadProgress {
  progress: number;
  status: 'idle' | 'uploading' | 'processing' | 'completed' | 'error';
  message?: string;
}

// Sync types
export interface SyncStatus {
  status: 'idle' | 'running' | 'completed' | 'failed';
  progress?: number;
  message?: string;
  last_sync_at?: string;
}