'use client';

import React from 'react';
import { useRouter } from 'next/navigation';
import { ShopifyOAuthCallback } from '@/components/shopify/ShopifyOAuthCallback';
import { ShopifyStore } from '@/types';

export default function ShopifyCallbackPage() {
  const router = useRouter();

  const handleSuccess = (store: ShopifyStore) => {
    // Redirect to Shopify dashboard page
    router.push('/dashboard/shopify');
  };

  const handleError = (error: string) => {
    // Redirect to Shopify page with error
    router.push(`/dashboard/shopify?error=${encodeURIComponent(error)}`);
  };

  return (
    <ShopifyOAuthCallback
      onSuccess={handleSuccess}
      onError={handleError}
    />
  );
}