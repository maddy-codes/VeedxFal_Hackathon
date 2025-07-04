'use client';

import { useEffect, useState } from 'react';
import { useAnalytics } from '@/contexts/AppContext';
import {
  TrendingUp,
  TrendingDown,
  DollarSign,
  Package,
  ShoppingCart,
  Users,
  Store,
  Plus
} from 'lucide-react';
import { ShopifyConnectionStatus } from '@/types';
import { apiClient } from '@/lib/api';
import Link from 'next/link';
import { Line } from 'react-chartjs-2';
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Legend,
  Filler,
} from 'chart.js';

// Register Chart.js components
ChartJS.register(
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Legend,
  Filler
);

interface MetricCardProps {
  title: string;
  value: string;
  change?: number;
  icon: React.ElementType;
  trend?: 'up' | 'down' | 'neutral';
}

function MetricCard({ title, value, change, icon: Icon, trend = 'neutral' }: MetricCardProps) {
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
        <div>
          <p className="text-sm font-medium text-gray-600">{title}</p>
          <p className="text-3xl font-bold text-gray-900">{value}</p>
          {change !== undefined && (
            <div className={`flex items-center mt-2 ${getTrendColor()}`}>
              {getTrendIcon()}
              <span className="text-sm font-medium ml-1">
                {change > 0 ? '+' : ''}{change.toFixed(1)}%
              </span>
              <span className="text-sm text-gray-500 ml-1">vs last month</span>
            </div>
          )}
        </div>
        <div className="flex-shrink-0">
          <Icon className="h-8 w-8 text-primary" />
        </div>
      </div>
    </div>
  );
}

export default function DashboardPage() {
  const { analytics, isLoading } = useAnalytics();
  const [chartData, setChartData] = useState<any>(null);
  const [shopifyStatus, setShopifyStatus] = useState<ShopifyConnectionStatus>({
    isConnected: false
  });

  useEffect(() => {
    // Generate sample chart data for monthly earnings
    const generateChartData = () => {
      const months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun'];
      const data = [8500, 9200, 8800, 10500, 11200, 12345];
      
      return {
        labels: months,
        datasets: [
          {
            label: 'Monthly Earnings',
            data: data,
            borderColor: '#427F8C',
            backgroundColor: 'rgba(66, 127, 140, 0.1)',
            borderWidth: 2,
            fill: true,
            tension: 0.4,
          },
        ],
      };
    };

    setChartData(generateChartData());
    loadShopifyStatus();
  }, []);

  const loadShopifyStatus = async () => {
    try {
      const stores = await apiClient.getShopifyStores() as any[];
      if (stores.length > 0) {
        const activeStore = stores.find((store: any) => store.is_active) || stores[0];
        const stats = await apiClient.getShopifyStoreStats(activeStore.id) as any;
        setShopifyStatus({
          isConnected: true,
          store: activeStore,
          stats,
          lastSync: stats?.last_sync_at,
          syncStatus: stats?.sync_status
        });
      }
    } catch (error) {
      // User might not have Shopify connected yet
      setShopifyStatus({ isConnected: false });
    }
  };

  const chartOptions = {
    responsive: true,
    maintainAspectRatio: false,
    plugins: {
      legend: {
        display: false,
      },
      title: {
        display: false,
      },
    },
    scales: {
      y: {
        beginAtZero: true,
        grid: {
          color: 'rgba(0, 0, 0, 0.1)',
        },
        ticks: {
          callback: function(value: any) {
            return '$' + value.toLocaleString();
          },
        },
      },
      x: {
        grid: {
          display: false,
        },
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
      {/* Overview Metrics */}
      <div>
        <h3 className="text-lg font-medium text-gray-900 mb-4">Overview</h3>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
          <MetricCard
            title="Total Revenue"
            value={`$${analytics.total_revenue.toLocaleString()}`}
            change={analytics.revenue_change_percent}
            trend={analytics.revenue_change_percent && analytics.revenue_change_percent > 0 ? 'up' : 'down'}
            icon={DollarSign}
          />
          <MetricCard
            title="Active Products"
            value={analytics.active_products.toString()}
            icon={Package}
          />
          <MetricCard
            title="Total Orders"
            value={analytics.total_orders.toString()}
            change={analytics.orders_change_percent}
            trend={analytics.orders_change_percent && analytics.orders_change_percent > 0 ? 'up' : 'down'}
            icon={ShoppingCart}
          />
          <MetricCard
            title="Avg Order Value"
            value={`$${analytics.avg_order_value.toFixed(2)}`}
            icon={Users}
          />
        </div>
      </div>

      {/* Shopify Connection Status */}
      <div className="bg-white rounded-lg shadow p-6">
        <div className="flex items-center justify-between mb-4">
          <h3 className="text-lg font-medium text-gray-900">Shopify Integration</h3>
          {shopifyStatus.isConnected ? (
            <Link href="/dashboard/shopify">
              <button className="btn btn-outline btn-sm">
                Manage Store
              </button>
            </Link>
          ) : (
            <Link href="/dashboard/shopify">
              <button className="btn btn-primary btn-sm">
                <Plus className="h-4 w-4 mr-2" />
                Connect Store
              </button>
            </Link>
          )}
        </div>
        
        {shopifyStatus.isConnected && shopifyStatus.store ? (
          <div className="flex items-center justify-between">
            <div className="flex items-center">
              <Store className="h-8 w-8 text-green-600 mr-3" />
              <div>
                <p className="font-medium text-gray-900">{shopifyStatus.store.shop_name}</p>
                <p className="text-sm text-gray-600">{shopifyStatus.store.shop_domain}</p>
              </div>
            </div>
            <div className="text-right">
              <div className="flex items-center text-green-600">
                <div className="w-2 h-2 bg-green-500 rounded-full mr-2"></div>
                <span className="text-sm font-medium">Connected</span>
              </div>
              {shopifyStatus.lastSync && (
                <p className="text-xs text-gray-500">
                  Last sync: {new Date(shopifyStatus.lastSync).toLocaleDateString()}
                </p>
              )}
            </div>
          </div>
        ) : (
          <div className="text-center py-8">
            <Store className="h-12 w-12 text-gray-400 mx-auto mb-4" />
            <p className="text-gray-600 mb-2">No Shopify store connected</p>
            <p className="text-sm text-gray-500">
              Connect your Shopify store to sync products and get AI-powered insights
            </p>
          </div>
        )}
      </div>

      {/* Charts Section */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
        {/* Monthly Earnings Chart */}
        <div className="bg-white rounded-lg shadow p-6">
          <h3 className="text-lg font-medium text-gray-900 mb-4">Monthly Earnings</h3>
          <div className="h-64">
            {chartData && (
              <Line data={chartData} options={chartOptions} />
            )}
          </div>
        </div>

        {/* Recent Activity */}
        <div className="bg-white rounded-lg shadow p-6">
          <h3 className="text-lg font-medium text-gray-900 mb-4">Recent Activity</h3>
          <div className="space-y-4">
            <div className="flex items-center justify-between py-3 border-b border-gray-200">
              <div className="flex items-center">
                <div className="w-2 h-2 bg-green-500 rounded-full mr-3"></div>
                <div>
                  <p className="text-sm font-medium text-gray-900">Product sync completed</p>
                  <p className="text-xs text-gray-500">2 minutes ago</p>
                </div>
              </div>
            </div>
            
            <div className="flex items-center justify-between py-3 border-b border-gray-200">
              <div className="flex items-center">
                <div className="w-2 h-2 bg-blue-500 rounded-full mr-3"></div>
                <div>
                  <p className="text-sm font-medium text-gray-900">New pricing recommendations</p>
                  <p className="text-xs text-gray-500">15 minutes ago</p>
                </div>
              </div>
            </div>
            
            <div className="flex items-center justify-between py-3 border-b border-gray-200">
              <div className="flex items-center">
                <div className="w-2 h-2 bg-yellow-500 rounded-full mr-3"></div>
                <div>
                  <p className="text-sm font-medium text-gray-900">Low inventory alert</p>
                  <p className="text-xs text-gray-500">1 hour ago</p>
                </div>
              </div>
            </div>
            
            <div className="flex items-center justify-between py-3">
              <div className="flex items-center">
                <div className="w-2 h-2 bg-purple-500 rounded-full mr-3"></div>
                <div>
                  <p className="text-sm font-medium text-gray-900">AI insights generated</p>
                  <p className="text-xs text-gray-500">3 hours ago</p>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Quick Actions */}
      <div className="bg-white rounded-lg shadow p-6">
        <h3 className="text-lg font-medium text-gray-900 mb-4">Quick Actions</h3>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <button className="btn btn-primary btn-md">
            Sync Products
          </button>
          <button className="btn btn-secondary btn-md">
            Generate AI Video
          </button>
          <button className="btn btn-outline btn-md">
            Export Report
          </button>
        </div>
      </div>
    </div>
  );
}