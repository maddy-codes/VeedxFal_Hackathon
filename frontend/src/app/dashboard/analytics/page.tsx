'use client';

import { useState, useEffect } from 'react';
import { useAnalytics } from '@/contexts/AppContext';
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

  // Revenue trend chart data
  const revenueChartData = {
    labels: ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun'],
    datasets: [
      {
        label: 'Revenue',
        data: [8500, 9200, 8800, 10500, 11200, 12345],
        borderColor: '#427F8C',
        backgroundColor: 'rgba(66, 127, 140, 0.1)',
        borderWidth: 3,
        fill: true,
        tension: 0.4,
      },
      {
        label: 'Target',
        data: [9000, 9500, 10000, 10500, 11000, 11500],
        borderColor: '#73B1BF',
        backgroundColor: 'transparent',
        borderWidth: 2,
        borderDash: [5, 5],
        fill: false,
        tension: 0.4,
      },
    ],
  };

  // Product performance chart data
  const productChartData = {
    labels: ['Wireless Earbuds', 'Classic Sneaker', 'Denim Jacket', 'Smartwatch', 'Phone Case'],
    datasets: [
      {
        label: 'Revenue',
        data: [3200, 2800, 2400, 4100, 1500],
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

  // Inventory status chart data
  const inventoryChartData = {
    labels: ['In Stock', 'Low Stock', 'Out of Stock'],
    datasets: [
      {
        data: [85, 12, 3],
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

  if (isLoading) {
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
          value="3.2%"
          change={0.5}
          trend="up"
          icon={Target}
          description="Visitors to customers"
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

        {/* Performance Metrics */}
        <div className="bg-white rounded-lg shadow p-6">
          <h3 className="text-lg font-medium text-gray-900 mb-4">Performance Metrics</h3>
          <div className="space-y-4">
            <div className="flex justify-between items-center">
              <span className="text-sm text-gray-600">Page Views</span>
              <span className="font-medium">24,567</span>
            </div>
            <div className="w-full bg-gray-200 rounded-full h-2">
              <div className="bg-primary h-2 rounded-full" style={{ width: '75%' }}></div>
            </div>

            <div className="flex justify-between items-center">
              <span className="text-sm text-gray-600">Unique Visitors</span>
              <span className="font-medium">8,432</span>
            </div>
            <div className="w-full bg-gray-200 rounded-full h-2">
              <div className="bg-secondary h-2 rounded-full" style={{ width: '60%' }}></div>
            </div>

            <div className="flex justify-between items-center">
              <span className="text-sm text-gray-600">Bounce Rate</span>
              <span className="font-medium">42%</span>
            </div>
            <div className="w-full bg-gray-200 rounded-full h-2">
              <div className="bg-yellow-500 h-2 rounded-full" style={{ width: '42%' }}></div>
            </div>

            <div className="flex justify-between items-center">
              <span className="text-sm text-gray-600">Session Duration</span>
              <span className="font-medium">3m 24s</span>
            </div>
            <div className="w-full bg-gray-200 rounded-full h-2">
              <div className="bg-green-500 h-2 rounded-full" style={{ width: '68%' }}></div>
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
                <p className="text-sm font-medium text-gray-900">Revenue Growth</p>
                <p className="text-xs text-gray-600">15.2% increase in monthly revenue compared to last month</p>
              </div>
            </div>
            <div className="flex items-start space-x-3">
              <div className="w-2 h-2 bg-blue-500 rounded-full mt-2"></div>
              <div>
                <p className="text-sm font-medium text-gray-900">Top Performer</p>
                <p className="text-xs text-gray-600">Smartwatch is your highest revenue generator this month</p>
              </div>
            </div>
            <div className="flex items-start space-x-3">
              <div className="w-2 h-2 bg-yellow-500 rounded-full mt-2"></div>
              <div>
                <p className="text-sm font-medium text-gray-900">Pricing Opportunity</p>
                <p className="text-xs text-gray-600">3 products identified as underpriced with high confidence</p>
              </div>
            </div>
          </div>
        </div>

        {/* Alerts */}
        <div className="bg-white rounded-lg shadow p-6">
          <h3 className="text-lg font-medium text-gray-900 mb-4">Alerts</h3>
          <div className="space-y-4">
            <div className="flex items-start space-x-3">
              <AlertTriangle className="h-5 w-5 text-red-500 mt-0.5" />
              <div>
                <p className="text-sm font-medium text-gray-900">Low Inventory</p>
                <p className="text-xs text-gray-600">5 products have less than 10 units in stock</p>
              </div>
            </div>
            <div className="flex items-start space-x-3">
              <AlertTriangle className="h-5 w-5 text-yellow-500 mt-0.5" />
              <div>
                <p className="text-sm font-medium text-gray-900">Price Competition</p>
                <p className="text-xs text-gray-600">Competitors have lowered prices on 2 similar products</p>
              </div>
            </div>
            <div className="flex items-start space-x-3">
              <TrendingUp className="h-5 w-5 text-green-500 mt-0.5" />
              <div>
                <p className="text-sm font-medium text-gray-900">Trending Product</p>
                <p className="text-xs text-gray-600">Denim Jacket showing strong upward trend</p>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}