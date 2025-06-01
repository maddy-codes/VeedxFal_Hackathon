'use client';

import React, { useState, useEffect } from 'react';
import { Button } from '@/components/ui/Button';
import { ShopifyStore, ShopifyStoreStats, ShopifySyncJob } from '@/types';
import { apiClient } from '@/lib/api';
import { 
  Store, 
  Package, 
  DollarSign, 
  ShoppingCart, 
  RefreshCw, 
  Clock, 
  CheckCircle, 
  AlertCircle,
  ExternalLink,
  Unlink
} from 'lucide-react';

interface ShopifyStoreDashboardProps {
  store: ShopifyStore;
  onStoreDisconnected: () => void;
}

export function ShopifyStoreDashboard({ store, onStoreDisconnected }: ShopifyStoreDashboardProps) {
  const [stats, setStats] = useState<ShopifyStoreStats | null>(null);
  const [syncJobs, setSyncJobs] = useState<ShopifySyncJob[]>([]);
  const [loading, setLoading] = useState(true);
  const [syncing, setSyncing] = useState(false);
  const [disconnecting, setDisconnecting] = useState(false);

  useEffect(() => {
    loadStoreData();
  }, [store.id]);

  const loadStoreData = async () => {
    try {
      setLoading(true);
      const [storeStats, jobs] = await Promise.all([
        apiClient.getShopifyStoreStats(store.id),
        apiClient.getShopifySyncJobs(store.id, 5)
      ]);
      setStats(storeStats as any);
      setSyncJobs(jobs as any);
    } catch (error) {
      console.error('Failed to load store data:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleSync = async () => {
    try {
      setSyncing(true);
      await apiClient.syncShopifyProducts(store.id, false);
      // Reload data after sync starts
      await loadStoreData();
    } catch (error) {
      console.error('Failed to start sync:', error);
    } finally {
      setSyncing(false);
    }
  };

  const handleDisconnect = async () => {
    if (!confirm('Are you sure you want to disconnect this Shopify store? This will remove all synced data.')) {
      return;
    }

    try {
      setDisconnecting(true);
      await apiClient.disconnectShopifyStore(store.id);
      onStoreDisconnected();
    } catch (error) {
      console.error('Failed to disconnect store:', error);
      setDisconnecting(false);
    }
  };

  const getSyncStatusColor = (status: string) => {
    switch (status) {
      case 'completed': return 'text-green-600';
      case 'running': return 'text-blue-600';
      case 'failed': return 'text-red-600';
      default: return 'text-gray-600';
    }
  };

  const getSyncStatusIcon = (status: string) => {
    switch (status) {
      case 'completed': return <CheckCircle className="h-4 w-4" />;
      case 'running': return <RefreshCw className="h-4 w-4 animate-spin" />;
      case 'failed': return <AlertCircle className="h-4 w-4" />;
      default: return <Clock className="h-4 w-4" />;
    }
  };

  if (loading) {
    return (
      <div className="bg-white rounded-lg shadow p-6">
        <div className="animate-pulse">
          <div className="h-6 bg-gray-200 rounded w-1/3 mb-4"></div>
          <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-6">
            {[...Array(4)].map((_, i) => (
              <div key={i} className="h-24 bg-gray-200 rounded"></div>
            ))}
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Store Header */}
      <div className="bg-white rounded-lg shadow p-6">
        <div className="flex items-center justify-between">
          <div className="flex items-center">
            <Store className="h-8 w-8 text-green-600 mr-3" />
            <div>
              <h2 className="text-xl font-semibold text-gray-900">{store.shop_name}</h2>
              <p className="text-sm text-gray-600">{store.shop_domain}</p>
            </div>
          </div>
          <div className="flex items-center space-x-3">
            <Button
              variant="outline"
              size="sm"
              onClick={() => window.open(`https://${store.shop_domain}`, '_blank')}
            >
              <ExternalLink className="h-4 w-4 mr-2" />
              Visit Store
            </Button>
            <Button
              variant="outline"
              size="sm"
              onClick={handleSync}
              loading={syncing}
              disabled={syncing}
            >
              <RefreshCw className="h-4 w-4 mr-2" />
              Sync Now
            </Button>
            <Button
              variant="destructive"
              size="sm"
              onClick={handleDisconnect}
              loading={disconnecting}
              disabled={disconnecting}
            >
              <Unlink className="h-4 w-4 mr-2" />
              Disconnect
            </Button>
          </div>
        </div>
      </div>

      {/* Store Statistics */}
      {stats && (
        <div className="bg-white rounded-lg shadow p-6">
          <h3 className="text-lg font-medium text-gray-900 mb-4">Store Overview</h3>
          <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
            <div className="text-center">
              <div className="flex items-center justify-center w-12 h-12 bg-blue-100 rounded-lg mx-auto mb-3">
                <Package className="h-6 w-6 text-blue-600" />
              </div>
              <p className="text-2xl font-bold text-gray-900">{stats.total_products}</p>
              <p className="text-sm text-gray-600">Total Products</p>
              <p className="text-xs text-green-600">{stats.active_products} active</p>
            </div>
            
            <div className="text-center">
              <div className="flex items-center justify-center w-12 h-12 bg-green-100 rounded-lg mx-auto mb-3">
                <DollarSign className="h-6 w-6 text-green-600" />
              </div>
              <p className="text-2xl font-bold text-gray-900">${stats.total_revenue.toLocaleString()}</p>
              <p className="text-sm text-gray-600">Total Revenue</p>
              <p className="text-xs text-gray-500">${stats.revenue_last_30_days.toLocaleString()} last 30d</p>
            </div>
            
            <div className="text-center">
              <div className="flex items-center justify-center w-12 h-12 bg-purple-100 rounded-lg mx-auto mb-3">
                <ShoppingCart className="h-6 w-6 text-purple-600" />
              </div>
              <p className="text-2xl font-bold text-gray-900">{stats.total_orders}</p>
              <p className="text-sm text-gray-600">Total Orders</p>
              <p className="text-xs text-gray-500">{stats.orders_last_30_days} last 30d</p>
            </div>
            
            <div className="text-center">
              <div className="flex items-center justify-center w-12 h-12 bg-orange-100 rounded-lg mx-auto mb-3">
                <RefreshCw className="h-6 w-6 text-orange-600" />
              </div>
              <p className="text-sm font-medium text-gray-900">Last Sync</p>
              <p className="text-xs text-gray-600">
                {stats.last_sync_at 
                  ? new Date(stats.last_sync_at).toLocaleDateString()
                  : 'Never'
                }
              </p>
              {stats.sync_status && (
                <div className={`flex items-center justify-center mt-1 ${getSyncStatusColor(stats.sync_status)}`}>
                  {getSyncStatusIcon(stats.sync_status)}
                  <span className="text-xs ml-1 capitalize">{stats.sync_status}</span>
                </div>
              )}
            </div>
          </div>
        </div>
      )}

      {/* Recent Sync Jobs */}
      <div className="bg-white rounded-lg shadow p-6">
        <h3 className="text-lg font-medium text-gray-900 mb-4">Recent Sync Activity</h3>
        {syncJobs.length > 0 ? (
          <div className="space-y-3">
            {syncJobs.map((job) => (
              <div key={job.id} className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
                <div className="flex items-center">
                  <div className={`mr-3 ${getSyncStatusColor(job.status)}`}>
                    {getSyncStatusIcon(job.status)}
                  </div>
                  <div>
                    <p className="text-sm font-medium text-gray-900 capitalize">
                      {job.sync_type.replace('_', ' ')}
                    </p>
                    <p className="text-xs text-gray-600">
                      {new Date(job.created_at).toLocaleString()}
                    </p>
                  </div>
                </div>
                <div className="text-right">
                  <p className={`text-sm font-medium capitalize ${getSyncStatusColor(job.status)}`}>
                    {job.status}
                  </p>
                  {job.progress !== undefined && (
                    <p className="text-xs text-gray-600">{job.progress}% complete</p>
                  )}
                  {job.processed_items !== undefined && job.total_items !== undefined && (
                    <p className="text-xs text-gray-600">
                      {job.processed_items}/{job.total_items} items
                    </p>
                  )}
                </div>
              </div>
            ))}
          </div>
        ) : (
          <p className="text-sm text-gray-600 text-center py-4">
            No sync activity yet. Click &quot;Sync Now&quot; to start syncing your products.
          </p>
        )}
      </div>
    </div>
  );
}