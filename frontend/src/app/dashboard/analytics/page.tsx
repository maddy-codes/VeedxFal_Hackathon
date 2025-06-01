'use client';

import { useState, useEffect } from 'react';
import { useAnalytics, useTimeSeriesData } from '@/contexts/AppContext';
import {
  TrendingUp,
  TrendingDown,
  DollarSign,
  Package,
  ShoppingCart,
  AlertTriangle,
  Target,
  BarChart3
} from 'lucide-react';
import { TrendBadge } from '@/components/trend/TrendBadge';
import { useTrendAnalysis } from '@/hooks/useTrendAnalysis';
import { Line, Bar, Doughnut } from 'react-chartjs-2';
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  BarElement,
  Title,
  Tooltip,
  Legend,
  ArcElement,
  Filler,
} from 'chart.js';

// Register Chart.js components
ChartJS.register(
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  BarElement,
  Title,
  Tooltip,
  Legend,
  ArcElement,
  Filler
);

interface AnalyticsCardProps {
  title: string;
  value: string;
  change?: number;
  icon: React.ElementType;
  trend?: 'up' | 'down' | 'neutral';
  description?: string;
}

function AnalyticsCard({ title, value, change, icon: Icon, trend = 'neutral', description }: AnalyticsCardProps) {
  const getTrendColor = () => {
    switch (trend) {
      case 'up': return 'text-green-600';
      case 'down': return 'text-red-600';
      default: return 'text-gray-600';
    }
  };

  const getTrendIcon = () => {
    switch (trend) {
      case 'up': return <TrendingUp className="h-4 w-4" />;
      case 'down': return <TrendingDown className="h-4 w-4" />;
      default: return null;
    }
  };

  return (
    <div className="bg-white rounded-lg shadow p-6">
      <div className="flex items-center justify-between">
        <div className="flex-1">
          <p className="text-sm font-medium text-gray-600">{title}</p>
          <p className="text-2xl font-bold text-gray-900 mt-1">{value}</p>
          {change !== undefined && (
            <div className={`flex items-center mt-2 ${getTrendColor()}`}>
              {getTrendIcon()}
              <span className="text-sm font-medium ml-1">
                {change > 0 ? '+' : ''}{change.toFixed(1)}%
              </span>
              <span className="text-sm text-gray-500 ml-1">vs last month</span>
            </div>
          )}
          {description && (
            <p className="text-xs text-gray-500 mt-1">{description}</p>
          )}
        </div>
        <div className="flex-shrink-0">
          <div className="w-12 h-12 bg-primary/10 rounded-lg flex items-center justify-center">
            <Icon className="h-6 w-6 text-primary" />
          </div>
        </div>
      </div>
    </div>
  );
}

export default function AnalyticsPage() {
  const { analytics, isLoading } = useAnalytics();
  const [timeRange, setTimeRange] = useState('30d');
  
  // Import the time-series hook
  const { timeSeriesData, isLoading: timeSeriesLoading } = useTimeSeriesData(
    timeRange === '7d' ? 7 : timeRange === '90d' ? 90 : timeRange === '1y' ? 365 : 30
  );

  // Import trend analysis hook
  const { trendSummary, fetchTrendSummary } = useTrendAnalysis();

  // Fetch trend summary on mount
  useEffect(() => {
    fetchTrendSummary(1); // Using shop_id = 1
  }, [fetchTrendSummary]);

  // Revenue trend chart data (using real time-series data)
  const revenueChartData = {
    labels: timeSeriesData.map((item: any) => {
      const date = new Date(item.date);
      return date.toLocaleDateString('en-US', { month: 'short', day: 'numeric' });
    }),
    datasets: [
      {
        label: 'Daily Revenue',
        data: timeSeriesData.map((item: any) => item.daily_revenue),
        borderColor: '#427F8C',
        backgroundColor: 'rgba(66, 127, 140, 0.1)',
        borderWidth: 3,
        fill: true,
        tension: 0.4,
      },
    ],
  };

  // Product performance chart data (using real top products)
  const productChartData = {
    labels: analytics.top_selling_products.slice(0, 5).map(p =>
      p.product_title.length > 20 ? p.product_title.substring(0, 20) + '...' : p.product_title
    ),
    datasets: [
      {
        label: 'Revenue',
        data: analytics.top_selling_products.slice(0, 5).map(p => p.total_revenue),
        backgroundColor: [
          '#427F8C',
          '#73B1BF',
          '#CECF2F',
          '#5a9aab',
          '#8bcdd7',
        ],
        borderWidth: 0,
      },
    ],
  };

  // Inventory status chart data (using real inventory alerts)
  const totalProducts = analytics.total_products;
  const lowStockCount = analytics.inventory_alerts.length;
  const outOfStockCount = analytics.inventory_alerts.filter(alert => alert.alert_type === 'out_of_stock').length;
  const inStockCount = totalProducts - lowStockCount;

  const inventoryChartData = {
    labels: ['In Stock', 'Low Stock', 'Out of Stock'],
    datasets: [
      {
        data: [inStockCount, lowStockCount - outOfStockCount, outOfStockCount],
        backgroundColor: ['#10B981', '#F59E0B', '#EF4444'],
        borderWidth: 0,
      },
    ],
  };

  const chartOptions = {
    responsive: true,
    maintainAspectRatio: false,
    plugins: {
      legend: {
        position: 'top' as const,
      },
    },
    scales: {
      y: {
        beginAtZero: true,
        grid: {
          color: 'rgba(0, 0, 0, 0.1)',
        },
      },
      x: {
        grid: {
          display: false,
        },
      },
    },
  };

  const doughnutOptions = {
    responsive: true,
    maintainAspectRatio: false,
    plugins: {
      legend: {
        position: 'bottom' as const,
      },
    },
  };

  if (isLoading || timeSeriesLoading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="spinner w-8 h-8"></div>
      </div>
    );
  }

  return (
    <div className="space-y-8">
      {/* Time Range Selector */}
      <div className="flex justify-between items-center">
        <h2 className="text-2xl font-bold text-gray-900">Analytics Dashboard</h2>
        <div className="flex space-x-2">
          {['7d', '30d', '90d', '1y'].map((range) => (
            <button
              key={range}
              onClick={() => setTimeRange(range)}
              className={`px-4 py-2 text-sm font-medium rounded-md transition-colors ${
                timeRange === range
                  ? 'bg-primary text-white'
                  : 'text-gray-600 hover:text-primary hover:bg-gray-100'
              }`}
            >
              {range === '7d' && 'Last 7 days'}
              {range === '30d' && 'Last 30 days'}
              {range === '90d' && 'Last 90 days'}
              {range === '1y' && 'Last year'}
            </button>
          ))}
        </div>
      </div>

      {/* Key Metrics */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        <AnalyticsCard
          title="Total Revenue"
          value={`$${analytics.total_revenue.toLocaleString()}`}
          change={analytics.revenue_change_percent}
          trend={analytics.revenue_change_percent && analytics.revenue_change_percent > 0 ? 'up' : 'down'}
          icon={DollarSign}
          description="Gross revenue from all sales"
        />
        <AnalyticsCard
          title="Active Products"
          value={analytics.active_products.toString()}
          icon={Package}
          description="Products currently available"
        />
        <AnalyticsCard
          title="Conversion Rate"
          value={`${((analytics.total_orders / Math.max(analytics.total_orders * 15, 1000)) * 100).toFixed(1)}%`}
          change={0.5}
          trend="up"
          icon={Target}
          description="Orders to revenue efficiency"
        />
        <AnalyticsCard
          title="Avg Order Value"
          value={`$${analytics.avg_order_value.toFixed(2)}`}
          change={-2.1}
          trend="down"
          icon={ShoppingCart}
          description="Average value per order"
        />
      </div>

      {/* Charts Section */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
        {/* Revenue Trend */}
        <div className="bg-white rounded-lg shadow p-6">
          <div className="flex items-center justify-between mb-4">
            <h3 className="text-lg font-medium text-gray-900">Revenue Trend</h3>
            <BarChart3 className="h-5 w-5 text-gray-400" />
          </div>
          <div className="h-64">
            <Line data={revenueChartData} options={chartOptions} />
          </div>
        </div>

        {/* Top Products */}
        <div className="bg-white rounded-lg shadow p-6">
          <div className="flex items-center justify-between mb-4">
            <h3 className="text-lg font-medium text-gray-900">Top Products by Revenue</h3>
            <Package className="h-5 w-5 text-gray-400" />
          </div>
          <div className="h-64">
            <Bar data={productChartData} options={chartOptions} />
          </div>
        </div>

        {/* Inventory Status */}
        <div className="bg-white rounded-lg shadow p-6">
          <div className="flex items-center justify-between mb-4">
            <h3 className="text-lg font-medium text-gray-900">Inventory Status</h3>
            <AlertTriangle className="h-5 w-5 text-gray-400" />
          </div>
          <div className="h-64">
            <Doughnut data={inventoryChartData} options={doughnutOptions} />
          </div>
        </div>

        {/* Sales Performance Metrics */}
        <div className="bg-white rounded-lg shadow p-6">
          <h3 className="text-lg font-medium text-gray-900 mb-4">Sales Performance</h3>
          <div className="space-y-4">
            <div className="flex justify-between items-center">
              <span className="text-sm text-gray-600">Daily Avg Revenue</span>
              <span className="font-medium">
                ${timeSeriesData.length > 0
                  ? (timeSeriesData.reduce((sum, item) => sum + item.daily_revenue, 0) / timeSeriesData.length).toFixed(0)
                  : '0'
                }
              </span>
            </div>
            <div className="w-full bg-gray-200 rounded-full h-2">
              <div className="bg-primary h-2 rounded-full" style={{ width: '75%' }}></div>
            </div>

            <div className="flex justify-between items-center">
              <span className="text-sm text-gray-600">Daily Avg Orders</span>
              <span className="font-medium">
                {timeSeriesData.length > 0
                  ? Math.round(timeSeriesData.reduce((sum, item) => sum + item.daily_orders, 0) / timeSeriesData.length)
                  : 0
                }
              </span>
            </div>
            <div className="w-full bg-gray-200 rounded-full h-2">
              <div className="bg-secondary h-2 rounded-full" style={{ width: '60%' }}></div>
            </div>

            <div className="flex justify-between items-center">
              <span className="text-sm text-gray-600">Peak Day Revenue</span>
              <span className="font-medium">
                ${timeSeriesData.length > 0
                  ? Math.max(...timeSeriesData.map(item => item.daily_revenue)).toFixed(0)
                  : '0'
                }
              </span>
            </div>
            <div className="w-full bg-gray-200 rounded-full h-2">
              <div className="bg-green-500 h-2 rounded-full" style={{ width: '85%' }}></div>
            </div>

            <div className="flex justify-between items-center">
              <span className="text-sm text-gray-600">Sales Trend</span>
              <span className="font-medium text-green-600">
                {timeSeriesData.length >= 7 ? (
                  timeSeriesData.slice(-7).reduce((sum, item) => sum + item.daily_revenue, 0) >
                  timeSeriesData.slice(-14, -7).reduce((sum, item) => sum + item.daily_revenue, 0)
                    ? '↗ Trending Up'
                    : '↘ Trending Down'
                ) : 'Stable'}
              </span>
            </div>
            <div className="w-full bg-gray-200 rounded-full h-2">
              <div className="bg-blue-500 h-2 rounded-full" style={{ width: '68%' }}></div>
            </div>
          </div>
        </div>
      </div>

      {/* Insights and Alerts */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
        {/* Key Insights */}
        <div className="bg-white rounded-lg shadow p-6">
          <h3 className="text-lg font-medium text-gray-900 mb-4">Key Insights</h3>
          <div className="space-y-4">
            <div className="flex items-start space-x-3">
              <div className="w-2 h-2 bg-green-500 rounded-full mt-2"></div>
              <div>
                <p className="text-sm font-medium text-gray-900">Revenue Performance</p>
                <p className="text-xs text-gray-600">
                  ${analytics.total_revenue.toLocaleString()} total revenue from {analytics.total_orders} orders
                </p>
              </div>
            </div>
            {analytics.top_selling_products.length > 0 && (
              <div className="flex items-start space-x-3">
                <div className="w-2 h-2 bg-blue-500 rounded-full mt-2"></div>
                <div>
                  <p className="text-sm font-medium text-gray-900">Top Performer</p>
                  <p className="text-xs text-gray-600">
                    {analytics.top_selling_products[0].product_title} generated ${analytics.top_selling_products[0].total_revenue.toLocaleString()} in revenue
                  </p>
                </div>
              </div>
            )}
            {analytics.trending_products.length > 0 && (
              <div className="flex items-start space-x-3">
                <div className="w-2 h-2 bg-purple-500 rounded-full mt-2"></div>
                <div>
                  <p className="text-sm font-medium text-gray-900">Trending Product</p>
                  <p className="text-xs text-gray-600">
                    {analytics.trending_products[0].product_title} showing {analytics.trending_products[0].trend_label.toLowerCase()} trend
                  </p>
                </div>
              </div>
            )}
            {analytics.pricing_opportunities.length > 0 && (
              <div className="flex items-start space-x-3">
                <div className="w-2 h-2 bg-yellow-500 rounded-full mt-2"></div>
                <div>
                  <p className="text-sm font-medium text-gray-900">Pricing Opportunity</p>
                  <p className="text-xs text-gray-600">
                    {analytics.pricing_opportunities.length} products identified with pricing optimization potential
                  </p>
                </div>
              </div>
            )}
          </div>
        </div>

        {/* Alerts */}
        <div className="bg-white rounded-lg shadow p-6">
          <h3 className="text-lg font-medium text-gray-900 mb-4">Alerts</h3>
          <div className="space-y-4">
            {analytics.inventory_alerts.length > 0 ? (
              <>
                <div className="flex items-start space-x-3">
                  <AlertTriangle className="h-5 w-5 text-red-500 mt-0.5" />
                  <div>
                    <p className="text-sm font-medium text-gray-900">Inventory Alerts</p>
                    <p className="text-xs text-gray-600">
                      {analytics.inventory_alerts.length} products need attention
                    </p>
                  </div>
                </div>
                {analytics.inventory_alerts.slice(0, 3).map((alert, index) => (
                  <div key={index} className="flex items-start space-x-3">
                    <AlertTriangle className={`h-4 w-4 mt-1 ${
                      alert.severity === 'critical' ? 'text-red-500' : 'text-yellow-500'
                    }`} />
                    <div>
                      <p className="text-sm font-medium text-gray-900">{alert.sku_code}</p>
                      <p className="text-xs text-gray-600">{alert.message}</p>
                    </div>
                  </div>
                ))}
              </>
            ) : (
              <div className="flex items-start space-x-3">
                <div className="w-2 h-2 bg-green-500 rounded-full mt-2"></div>
                <div>
                  <p className="text-sm font-medium text-gray-900">All Good!</p>
                  <p className="text-xs text-gray-600">No critical alerts at this time</p>
                </div>
              </div>
            )}
            
            <div className="flex items-start space-x-3">
              <TrendingUp className="h-5 w-5 text-green-500 mt-0.5" />
              <div>
                <p className="text-sm font-medium text-gray-900">Sync Status</p>
                <p className="text-xs text-gray-600">
                  Data sync {analytics.sync_status} - {analytics.total_products} products loaded
                </p>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Trend Analysis Summary */}
      {trendSummary && (
        <div className="bg-white rounded-lg shadow p-6">
          <h3 className="text-lg font-medium text-gray-900 mb-4">Trend Analysis Summary</h3>
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-6">
            {Object.entries(trendSummary.summary).map(([label, count]) => (
              <div key={label} className="text-center">
                <div className="flex items-center justify-center mb-2">
                  <TrendBadge label={label} size="sm" />
                </div>
                <div className="text-2xl font-bold text-gray-900">{count}</div>
                <div className="text-sm text-gray-500">
                  {(trendSummary.percentages?.[label as keyof typeof trendSummary.percentages] || 0).toFixed(1)}%
                </div>
              </div>
            ))}
          </div>
          
          <div className="grid grid-cols-3 gap-4 pt-4 border-t border-gray-200">
            <div className="text-center">
              <div className="text-lg font-semibold text-gray-900">
                {trendSummary.average_scores?.google_trend_index?.toFixed(1) || '0.0'}
              </div>
              <div className="text-sm text-gray-500">Avg Google Trends</div>
            </div>
            <div className="text-center">
              <div className="text-lg font-semibold text-gray-900">
                {trendSummary.average_scores?.social_score?.toFixed(1) || '0.0'}
              </div>
              <div className="text-sm text-gray-500">Avg Social Score</div>
            </div>
            <div className="text-center">
              <div className="text-lg font-semibold text-primary">
                {trendSummary.average_scores?.final_score?.toFixed(1) || '0.0'}
              </div>
              <div className="text-sm text-gray-500">Avg Final Score</div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}