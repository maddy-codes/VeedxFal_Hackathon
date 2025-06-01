'use client';

import React, { useEffect, useState } from 'react';
import { useSearchParams, useRouter } from 'next/navigation';
import { ShopifyStore } from '@/types';
import { apiClient } from '@/lib/api';
import { CheckCircle, AlertCircle, Loader } from 'lucide-react';

interface ShopifyOAuthCallbackProps {
  onSuccess: (store: ShopifyStore) => void;
  onError: (error: string) => void;
}

export function ShopifyOAuthCallback({ onSuccess, onError }: ShopifyOAuthCallbackProps) {
  const searchParams = useSearchParams();
  const router = useRouter();
  const [status, setStatus] = useState<'processing' | 'success' | 'error'>('processing');
  const [message, setMessage] = useState('Processing Shopify connection...');

  useEffect(() => {
    handleOAuthCallback();
  }, []);

  const handleOAuthCallback = async () => {
    try {
      const code = searchParams.get('code');
      const shop = searchParams.get('shop');
      const state = searchParams.get('state');
      const error = searchParams.get('error');

      if (error) {
        throw new Error(`OAuth error: ${error}`);
      }

      if (!code || !shop) {
        throw new Error('Missing required OAuth parameters');
      }

      setMessage('Exchanging authorization code...');

      // Handle OAuth callback
      const store = await apiClient.handleShopifyOAuthCallback(shop, code, state || undefined) as any;

      setStatus('success');
      setMessage('Successfully connected to Shopify!');
      
      // Wait a moment to show success message
      setTimeout(() => {
        onSuccess(store);
      }, 1500);

    } catch (err: any) {
      console.error('OAuth callback error:', err);
      setStatus('error');
      setMessage(err.response?.data?.detail || err.message || 'Failed to connect to Shopify');
      onError(err.response?.data?.detail || err.message || 'Failed to connect to Shopify');
    }
  };

  const getStatusIcon = () => {
    switch (status) {
      case 'processing':
        return <Loader className="h-8 w-8 text-blue-600 animate-spin" />;
      case 'success':
        return <CheckCircle className="h-8 w-8 text-green-600" />;
      case 'error':
        return <AlertCircle className="h-8 w-8 text-red-600" />;
    }
  };

  const getStatusColor = () => {
    switch (status) {
      case 'processing':
        return 'text-blue-600';
      case 'success':
        return 'text-green-600';
      case 'error':
        return 'text-red-600';
    }
  };

  return (
    <div className="min-h-screen flex items-center justify-center bg-gray-50">
      <div className="bg-white rounded-lg shadow-lg p-8 max-w-md w-full mx-4">
        <div className="text-center">
          <div className="flex justify-center mb-4">
            {getStatusIcon()}
          </div>
          
          <h2 className={`text-xl font-semibold mb-2 ${getStatusColor()}`}>
            {status === 'processing' && 'Connecting to Shopify'}
            {status === 'success' && 'Connection Successful!'}
            {status === 'error' && 'Connection Failed'}
          </h2>
          
          <p className="text-gray-600 mb-6">{message}</p>
          
          {status === 'error' && (
            <button
              onClick={() => router.push('/dashboard')}
              className="bg-primary text-white px-4 py-2 rounded-md hover:bg-primary/90 transition-colors"
            >
              Return to Dashboard
            </button>
          )}
          
          {status === 'processing' && (
            <div className="flex justify-center">
              <div className="animate-pulse text-sm text-gray-500">
                Please wait while we set up your connection...
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}