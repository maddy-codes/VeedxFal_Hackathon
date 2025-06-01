'use client';

import React, { useState, useEffect } from 'react';
import { ShopifySyncJob } from '@/types';
import { apiClient } from '@/lib/api';
import { RefreshCw, CheckCircle, AlertCircle, Clock } from 'lucide-react';

interface ShopifySyncProgressProps {
  shopId: number;
  onSyncComplete?: () => void;
  className?: string;
}

export function ShopifySyncProgress({ shopId, onSyncComplete, className = '' }: ShopifySyncProgressProps) {
  const [currentSync, setCurrentSync] = useState<ShopifySyncJob | null>(null);
  const [isPolling, setIsPolling] = useState(false);

  useEffect(() => {
    checkForActiveSync();
  }, [shopId]);

  useEffect(() => {
    let interval: NodeJS.Timeout;

    if (currentSync && (currentSync.status === 'running' || currentSync.status === 'pending')) {
      setIsPolling(true);
      interval = setInterval(checkSyncStatus, 2000); // Poll every 2 seconds
    } else {
      setIsPolling(false);
    }

    return () => {
      if (interval) clearInterval(interval);
    };
  }, [currentSync]);

  const checkForActiveSync = async () => {
    try {
      const jobs = await apiClient.getShopifySyncJobs(shopId, 1) as any[];
      if (jobs.length > 0) {
        const latestJob = jobs[0];
        if (latestJob.status === 'running' || latestJob.status === 'pending') {
          setCurrentSync(latestJob);
        }
      }
    } catch (error) {
      console.error('Failed to check sync status:', error);
    }
  };

  const checkSyncStatus = async () => {
    if (!currentSync) return;

    try {
      const jobs = await apiClient.getShopifySyncJobs(shopId, 1) as any[];
      if (jobs.length > 0) {
        const updatedJob = jobs[0];
        setCurrentSync(updatedJob);

        if (updatedJob.status === 'completed' || updatedJob.status === 'failed') {
          setIsPolling(false);
          if (updatedJob.status === 'completed' && onSyncComplete) {
            onSyncComplete();
          }
        }
      }
    } catch (error) {
      console.error('Failed to update sync status:', error);
    }
  };

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'running':
        return <RefreshCw className="h-4 w-4 animate-spin text-blue-600" />;
      case 'completed':
        return <CheckCircle className="h-4 w-4 text-green-600" />;
      case 'failed':
        return <AlertCircle className="h-4 w-4 text-red-600" />;
      case 'pending':
        return <Clock className="h-4 w-4 text-yellow-600" />;
      default:
        return null;
    }
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'running':
        return 'text-blue-600 bg-blue-50 border-blue-200';
      case 'completed':
        return 'text-green-600 bg-green-50 border-green-200';
      case 'failed':
        return 'text-red-600 bg-red-50 border-red-200';
      case 'pending':
        return 'text-yellow-600 bg-yellow-50 border-yellow-200';
      default:
        return 'text-gray-600 bg-gray-50 border-gray-200';
    }
  };

  const getProgressPercentage = () => {
    if (!currentSync) return 0;
    if (currentSync.progress !== undefined) return currentSync.progress;
    if (currentSync.processed_items !== undefined && currentSync.total_items !== undefined) {
      return Math.round((currentSync.processed_items / currentSync.total_items) * 100);
    }
    return 0;
  };

  if (!currentSync || (currentSync.status !== 'running' && currentSync.status !== 'pending')) {
    return null;
  }

  const progress = getProgressPercentage();

  return (
    <div className={`border rounded-lg p-4 ${getStatusColor(currentSync.status)} ${className}`}>
      <div className="flex items-center justify-between mb-3">
        <div className="flex items-center">
          {getStatusIcon(currentSync.status)}
          <span className="ml-2 font-medium capitalize">
            {currentSync.sync_type.replace('_', ' ')} in Progress
          </span>
        </div>
        <span className="text-sm font-medium">{progress}%</span>
      </div>

      {/* Progress Bar */}
      <div className="w-full bg-gray-200 rounded-full h-2 mb-2">
        <div
          className="bg-current h-2 rounded-full transition-all duration-300 ease-out"
          style={{ width: `${progress}%` }}
        ></div>
      </div>

      {/* Progress Details */}
      <div className="flex justify-between text-xs">
        <span>
          {currentSync.processed_items !== undefined && currentSync.total_items !== undefined
            ? `${currentSync.processed_items} of ${currentSync.total_items} items`
            : 'Processing...'
          }
        </span>
        <span>
          Started {new Date(currentSync.created_at).toLocaleTimeString()}
        </span>
      </div>

      {/* Status Message */}
      {currentSync.status === 'pending' && (
        <p className="text-xs mt-2 opacity-75">
          Sync job is queued and will start shortly...
        </p>
      )}

      {currentSync.status === 'running' && (
        <p className="text-xs mt-2 opacity-75">
          Syncing your products from Shopify...
        </p>
      )}
    </div>
  );
}