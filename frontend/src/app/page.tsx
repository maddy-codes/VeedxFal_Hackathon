'use client';

import { useEffect } from 'react';
import { useAuth } from '@/contexts/AuthContext';

export default function HomePage() {
  const { user, isLoading } = useAuth();

  useEffect(() => {
    if (!isLoading) {
      if (user) {
        // Redirect authenticated users to dashboard
        window.location.href = '/dashboard';
      } else {
        // Redirect unauthenticated users to login
        window.location.href = '/auth/login';
      }
    }
  }, [user, isLoading]);

  if (isLoading) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-background">
        <div className="text-center">
          <div className="spinner w-16 h-16 mx-auto mb-4"></div>
          <h2 className="text-xl font-semibold text-primary">Loading Retail AI Advisor...</h2>
          <p className="text-gray-600 mt-2">Please wait while we initialize your session</p>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen flex items-center justify-center bg-background">
      <div className="text-center">
        <div className="spinner w-16 h-16 mx-auto mb-4"></div>
        <h2 className="text-xl font-semibold text-primary">Redirecting...</h2>
      </div>
    </div>
  );
}
