'use client';

import { ReactNode } from 'react';
import { useAuth, withAuth } from '@/contexts/AuthContext';
import {
  Home,
  BarChart3,
  TrendingUp,
  Settings,
  LogOut,
  Menu,
  X,
  Store
} from 'lucide-react';
import { useState } from 'react';
import Link from 'next/link';
import { usePathname } from 'next/navigation';

interface DashboardLayoutProps {
  children: ReactNode;
}

const sidebarItems = [
  { name: 'Dashboard', href: '/dashboard', icon: Home },
  { name: 'Shopify Integration', href: '/dashboard/shopify', icon: Store },
  { name: 'Product Insights', href: '/dashboard/insights', icon: TrendingUp },
  { name: 'Pricing Calculator', href: '/dashboard/pricing', icon: BarChart3 },
  { name: 'Analytics', href: '/dashboard/analytics', icon: BarChart3 },
  { name: 'Settings', href: '/dashboard/settings', icon: Settings },
];

function DashboardLayout({ children }: DashboardLayoutProps) {
  const [sidebarOpen, setSidebarOpen] = useState(false);
  const { user, logout } = useAuth();
  const pathname = usePathname();

  const handleLogout = async () => {
    try {
      await logout();
      window.location.href = '/auth/login';
    } catch (error) {
      console.error('Logout error:', error);
    }
  };

  return (
    <div className="min-h-screen bg-background flex">
      {/* Mobile sidebar overlay */}
      {sidebarOpen && (
        <div
          className="fixed inset-0 z-40 lg:hidden"
          onClick={() => setSidebarOpen(false)}
        >
          <div className="fixed inset-0 bg-black opacity-50"></div>
        </div>
      )}

      {/* Sidebar */}
      <div className={`
        fixed inset-y-0 left-0 z-50 w-64 bg-primary transform transition-transform duration-300 ease-in-out
        ${sidebarOpen ? 'translate-x-0' : '-translate-x-full'}
        lg:translate-x-0 lg:relative lg:flex lg:flex-col
      `}>
        <div className="flex items-center justify-between h-16 px-6 bg-primary-600">
          <h1 className="text-xl font-bold text-white">Retail AI Advisor</h1>
          <button
            onClick={() => setSidebarOpen(false)}
            className="lg:hidden text-white hover:text-gray-300"
          >
            <X className="h-6 w-6" />
          </button>
        </div>

        <nav className="mt-8">
          <div className="px-4 space-y-2">
            {sidebarItems.map((item) => {
              const Icon = item.icon;
              const isActive = pathname === item.href;
              
              return (
                <Link
                  key={item.name}
                  href={item.href}
                  className={`
                    flex items-center px-4 py-3 text-sm font-medium rounded-lg transition-colors
                    ${isActive 
                      ? 'bg-primary-700 text-white border-r-4 border-white' 
                      : 'text-gray-200 hover:bg-primary-600 hover:text-white'
                    }
                  `}
                  onClick={() => setSidebarOpen(false)}
                >
                  <Icon className="mr-3 h-5 w-5" />
                  {item.name}
                </Link>
              );
            })}
          </div>

          <div className="mt-8 pt-8 border-t border-primary-600">
            <div className="px-4">
              <div className="flex items-center px-4 py-3 text-sm text-gray-200">
                <div className="flex-shrink-0">
                  <div className="w-8 h-8 bg-primary-700 rounded-full flex items-center justify-center">
                    <span className="text-white font-medium">
                      {user?.email?.charAt(0).toUpperCase()}
                    </span>
                  </div>
                </div>
                <div className="ml-3">
                  <p className="text-sm font-medium text-white truncate">
                    {user?.email}
                  </p>
                </div>
              </div>
              
              <button
                onClick={handleLogout}
                className="flex items-center w-full px-4 py-3 text-sm font-medium text-gray-200 rounded-lg hover:bg-primary-600 hover:text-white transition-colors"
              >
                <LogOut className="mr-3 h-5 w-5" />
                Log out
              </button>
            </div>
          </div>
        </nav>
      </div>

      {/* Main content */}
      <div className="flex-1 flex flex-col lg:pl-0">
        {/* Top bar */}
        <div className="sticky top-0 z-40 flex h-16 shrink-0 items-center gap-x-4 border-b border-gray-200 bg-white px-4 shadow-sm sm:gap-x-6 sm:px-6 lg:px-8">
          <button
            type="button"
            className="-m-2.5 p-2.5 text-gray-700 lg:hidden"
            onClick={() => setSidebarOpen(true)}
          >
            <Menu className="h-6 w-6" />
          </button>

          <div className="flex flex-1 gap-x-4 self-stretch lg:gap-x-6">
            <div className="flex flex-1 items-center">
              <h2 className="text-2xl font-bold text-gray-900">
                {pathname === '/dashboard' && 'Dashboard Overview'}
                {pathname === '/dashboard/shopify' && 'Shopify Integration'}
                {pathname === '/dashboard/insights' && 'Product Insights'}
                {pathname === '/dashboard/pricing' && 'Cost-Plus Pricing Calculator'}
                {pathname === '/dashboard/analytics' && 'Analytics'}
                {pathname === '/dashboard/settings' && 'Settings'}
              </h2>
            </div>
            
            <div className="flex items-center gap-x-4 lg:gap-x-6">
              <button
                onClick={handleLogout}
                className="btn btn-outline btn-sm"
              >
                Log out
              </button>
            </div>
          </div>
        </div>

        {/* Page content */}
        <main className="py-8">
          <div className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8">
            {children}
          </div>
        </main>
      </div>
    </div>
  );
}

export default withAuth(DashboardLayout);