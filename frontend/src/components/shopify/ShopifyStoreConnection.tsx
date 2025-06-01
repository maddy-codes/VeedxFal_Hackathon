'use client';

import React, { useState } from 'react';
import { Button } from '@/components/ui/Button';
import { Input } from '@/components/ui/Input';
import { ShopifyStore } from '@/types';
import { apiClient } from '@/lib/api';
import { Store, ExternalLink, AlertCircle } from 'lucide-react';

interface ShopifyStoreConnectionProps {
  onStoreConnected: (store: ShopifyStore) => void;
  isLoading?: boolean;
}

export function ShopifyStoreConnection({ onStoreConnected, isLoading = false }: ShopifyStoreConnectionProps) {
  const [shopDomain, setShopDomain] = useState('');
  const [connecting, setConnecting] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleConnect = async () => {
    if (!shopDomain.trim()) {
      setError('Please enter your Shopify store domain');
      return;
    }

    // Clean up domain input
    let domain = shopDomain.trim().toLowerCase();
    if (domain.startsWith('http://') || domain.startsWith('https://')) {
      domain = domain.replace(/^https?:\/\//, '');
    }
    if (domain.endsWith('.myshopify.com')) {
      domain = domain.replace('.myshopify.com', '');
    }
    domain = domain.replace(/[^a-z0-9-]/g, '');

    if (!domain) {
      setError('Please enter a valid Shopify store domain');
      return;
    }

    const fullDomain = `${domain}.myshopify.com`;

    try {
      setConnecting(true);
      setError(null);

      // Generate OAuth URL
      const oauthData = await apiClient.generateShopifyOAuthUrl(fullDomain) as any;
      
      // Redirect to Shopify OAuth
      window.location.href = oauthData.oauth_url;
      
    } catch (err: any) {
      console.error('OAuth URL generation error:', err);
      setError(err.response?.data?.detail || 'Failed to connect to Shopify. Please check your store domain.');
      setConnecting(false);
    }
  };

  const handleDomainChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    setShopDomain(e.target.value);
    if (error) setError(null);
  };

  return (
    <div className="bg-white rounded-lg shadow p-6">
      <div className="flex items-center mb-4">
        <Store className="h-6 w-6 text-green-600 mr-2" />
        <h3 className="text-lg font-medium text-gray-900">Connect Your Shopify Store</h3>
      </div>
      
      <p className="text-sm text-gray-600 mb-6">
        Connect your Shopify store to sync products, track inventory, and get AI-powered pricing insights.
      </p>

      <div className="space-y-4">
        <div>
          <Input
            label="Shopify Store Domain"
            placeholder="your-store-name"
            value={shopDomain}
            onChange={handleDomainChange}
            error={error || undefined}
            disabled={connecting || isLoading}
            icon={<ExternalLink className="h-4 w-4 text-gray-400" />}
          />
          <p className="text-xs text-gray-500 mt-1">
            Enter your store name (e.g., &quot;my-store&quot; for my-store.myshopify.com)
          </p>
        </div>

        {error && (
          <div className="flex items-center p-3 bg-red-50 border border-red-200 rounded-md">
            <AlertCircle className="h-4 w-4 text-red-600 mr-2" />
            <p className="text-sm text-red-700">{error}</p>
          </div>
        )}

        <Button
          onClick={handleConnect}
          loading={connecting || isLoading}
          disabled={!shopDomain.trim() || connecting || isLoading}
          className="w-full"
        >
          {connecting ? 'Connecting...' : 'Connect to Shopify'}
        </Button>
      </div>

      <div className="mt-6 p-4 bg-blue-50 border border-blue-200 rounded-md">
        <h4 className="text-sm font-medium text-blue-900 mb-2">What happens next?</h4>
        <ul className="text-xs text-blue-800 space-y-1">
          <li>• You&apos;ll be redirected to Shopify to authorize the connection</li>
          <li>• We&apos;ll sync your products and inventory data</li>
          <li>• You&apos;ll get access to AI-powered pricing recommendations</li>
          <li>• Real-time sync keeps your data up to date</li>
        </ul>
      </div>
    </div>
  );
}