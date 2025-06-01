'use client';

import React, { useState, useEffect } from 'react';
import { useAuth } from '@/contexts/AuthContext';
import { ShopifyStore, ShopifyConnectionStatus } from '@/types';
import { ShopifyStoreConnection } from '@/components/shopify/ShopifyStoreConnection';
import { ShopifyStoreDashboard } from '@/components/shopify/ShopifyStoreDashboard';
import { ShopifySyncProgress } from '@/components/shopify/ShopifySyncProgress';
import { apiClient } from '@/lib/api';
import { Store, AlertCircle } from 'lucide-react';

export default function ShopifyPage() {
  const { user } = useAuth();
  const [connectionStatus, setConnectionStatus] = useState<ShopifyConnectionStatus>({
    isConnected: false
  });
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (user) {
      loadShopifyStores();
    }
  }, [user]);

  const loadShopifyStores = async () => {
    try {
      setLoading(true);
      setError(null);
      
      const stores = await apiClient.getShopifyStores() as any[];
      
      if (stores.length > 0) {
        const activeStore = stores.find((store: any) => store.is_active) || stores[0];
        const stats = await apiClient.getShopifyStoreStats(activeStore.id) as any;
        
        setConnectionStatus({
          isConnected: true,
          store: activeStore,
          stats,
          lastSync: stats?.last_sync_at,
          syncStatus: stats?.sync_status
        });
      } else {
        setConnectionStatus({ isConnected: false });
      }
    } catch (err: any) {
      console.error('Failed to load Shopify stores:', err);
      setError(err.response?.data?.detail || 'Failed to load Shopify connection status');
      setConnectionStatus({ isConnected: false });
    } finally {
      setLoading(false);
    }
  };

  const handleStoreConnected = (store: ShopifyStore) => {
    setConnectionStatus({
      isConnected: true,
      store
    });
    // Reload to get stats
    loadShopifyStores();
  };

  const handleStoreDisconnected = () => {
    setConnectionStatus({ isConnected: false });
  };

  const handleSyncComplete = () => {
    // Reload store data when sync completes
    if (connectionStatus.store) {
      loadShopifyStores();
    }
  };

  if (loading) {
    return (
      <div className="space-y-6">
        <div className="flex items-center">
          <Store className="h-8 w-8 text-green-600 mr-3" />
          <div>
            <h1 className="text-2xl font-bold text-gray-900">Shopify Integration</h1>
            <p className="text-gray-600">Connect and manage your Shopify store</p>
          </div>
        </div>
        
        <div className="bg-white rounded-lg shadow p-6">
          <div className="animate-pulse">
            <div className="h-6 bg-gray-200 rounded w-1/3 mb-4"></div>
            <div className="h-32 bg-gray-200 rounded"></div>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Page Header */}
      <div className="flex items-center justify-between">
        <div className="flex items-center">
          <Store className="h-8 w-8 text-green-600 mr-3" />
          <div>
            <h1 className="text-2xl font-bold text-gray-900">Shopify Integration</h1>
            <p className="text-gray-600">
              {connectionStatus.isConnected 
                ? 'Manage your connected Shopify store'
                : 'Connect your Shopify store to get started'
              }
            </p>
          </div>
        </div>
      </div>

      {/* Error Message */}
      {error && (
        <div className="bg-red-50 border border-red-200 rounded-lg p-4">
          <div className="flex items-center">
            <AlertCircle className="h-5 w-5 text-red-600 mr-2" />
            <p className="text-red-700">{error}</p>
          </div>
        </div>
      )}

      {/* Sync Progress */}
      {connectionStatus.isConnected && connectionStatus.store && (
        <ShopifySyncProgress
          shopId={connectionStatus.store.id}
          onSyncComplete={handleSyncComplete}
        />
      )}

      {/* Main Content */}
      {connectionStatus.isConnected && connectionStatus.store ? (
        <ShopifyStoreDashboard
          store={connectionStatus.store}
          onStoreDisconnected={handleStoreDisconnected}
        />
      ) : (
        <ShopifyStoreConnection
          onStoreConnected={handleStoreConnected}
          isLoading={loading}
        />
      )}

      {/* Help Section */}
      <div className="bg-blue-50 border border-blue-200 rounded-lg p-6">
        <h3 className="text-lg font-medium text-blue-900 mb-3">Need Help?</h3>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4 text-sm text-blue-800">
          <div>
            <h4 className="font-medium mb-2">Getting Started</h4>
            <ul className="space-y-1">
              <li>• Enter your Shopify store domain</li>
              <li>• Authorize the connection in Shopify</li>
              <li>• Wait for initial product sync</li>
              <li>• Start getting AI-powered insights</li>
            </ul>
          </div>
          <div>
            <h4 className="font-medium mb-2">Features</h4>
            <ul className="space-y-1">
              <li>• Real-time product synchronization</li>
              <li>• Inventory level monitoring</li>
              <li>• AI-powered pricing recommendations</li>
              <li>• Sales analytics and insights</li>
            </ul>
          </div>
        </div>
      </div>
    </div>
  );
}