'use client';

import { useState } from 'react';
import { useAuth } from '@/contexts/AuthContext';
import { 
  User, 
  Store, 
  Bell, 
  Shield, 
  Upload, 
  Download,
  Trash2,
  Save,
  Eye,
  EyeOff
} from 'lucide-react';

interface SettingsSectionProps {
  title: string;
  description: string;
  icon: React.ElementType;
  children: React.ReactNode;
}

function SettingsSection({ title, description, icon: Icon, children }: SettingsSectionProps) {
  return (
    <div className="bg-white rounded-lg shadow p-6">
      <div className="flex items-center mb-4">
        <div className="w-10 h-10 bg-primary/10 rounded-lg flex items-center justify-center mr-4">
          <Icon className="h-5 w-5 text-primary" />
        </div>
        <div>
          <h3 className="text-lg font-medium text-gray-900">{title}</h3>
          <p className="text-sm text-gray-600">{description}</p>
        </div>
      </div>
      {children}
    </div>
  );
}

export default function SettingsPage() {
  const { user, store } = useAuth();
  const [showPassword, setShowPassword] = useState(false);
  const [notifications, setNotifications] = useState({
    email: true,
    push: false,
    sms: false,
    marketing: true,
  });

  const handleNotificationChange = (type: keyof typeof notifications) => {
    setNotifications(prev => ({
      ...prev,
      [type]: !prev[type]
    }));
  };

  const handleSaveProfile = () => {
    // TODO: Implement profile save
    console.log('Saving profile...');
  };

  const handleChangePassword = () => {
    // TODO: Implement password change
    console.log('Changing password...');
  };

  const handleExportData = () => {
    // TODO: Implement data export
    console.log('Exporting data...');
  };

  const handleDeleteAccount = () => {
    // TODO: Implement account deletion
    if (confirm('Are you sure you want to delete your account? This action cannot be undone.')) {
      console.log('Deleting account...');
    }
  };

  return (
    <div className="space-y-8">
      <div>
        <h2 className="text-2xl font-bold text-gray-900 mb-2">Settings</h2>
        <p className="text-gray-600">Manage your account settings and preferences</p>
      </div>

      <div className="space-y-6">
        {/* Profile Settings */}
        <SettingsSection
          title="Profile Information"
          description="Update your personal information and account details"
          icon={User}
        >
          <div className="space-y-4">
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <label className="form-label">Full Name</label>
                <input
                  type="text"
                  className="input"
                  defaultValue={user?.user_metadata?.full_name || ''}
                  placeholder="Enter your full name"
                />
              </div>
              <div>
                <label className="form-label">Email Address</label>
                <input
                  type="email"
                  className="input"
                  defaultValue={user?.email || ''}
                  placeholder="Enter your email"
                />
              </div>
            </div>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <label className="form-label">Phone Number</label>
                <input
                  type="tel"
                  className="input"
                  placeholder="Enter your phone number"
                />
              </div>
              <div>
                <label className="form-label">Time Zone</label>
                <select className="input">
                  <option>UTC-8 (Pacific Time)</option>
                  <option>UTC-5 (Eastern Time)</option>
                  <option>UTC+0 (GMT)</option>
                  <option>UTC+1 (Central European Time)</option>
                </select>
              </div>
            </div>
            <div className="flex justify-end">
              <button onClick={handleSaveProfile} className="btn btn-primary btn-md">
                <Save className="h-4 w-4 mr-2" />
                Save Changes
              </button>
            </div>
          </div>
        </SettingsSection>

        {/* Store Settings */}
        <SettingsSection
          title="Store Configuration"
          description="Manage your store settings and integrations"
          icon={Store}
        >
          <div className="space-y-4">
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <label className="form-label">Store Name</label>
                <input
                  type="text"
                  className="input"
                  defaultValue={store?.shop_name || ''}
                  placeholder="Enter store name"
                />
              </div>
              <div>
                <label className="form-label">Store Domain</label>
                <input
                  type="text"
                  className="input"
                  defaultValue={store?.shop_domain || ''}
                  placeholder="yourstore.myshopify.com"
                />
              </div>
            </div>
            <div>
              <label className="form-label">Store Description</label>
              <textarea
                className="input min-h-[100px]"
                placeholder="Describe your store..."
              />
            </div>
            <div className="flex justify-between items-center">
              <div>
                <h4 className="font-medium text-gray-900">Shopify Integration</h4>
                <p className="text-sm text-gray-600">
                  {store ? 'Connected' : 'Not connected'}
                </p>
              </div>
              <button className="btn btn-outline btn-md">
                {store ? 'Reconnect' : 'Connect Shopify'}
              </button>
            </div>
          </div>
        </SettingsSection>

        {/* Security Settings */}
        <SettingsSection
          title="Security & Privacy"
          description="Manage your password and security preferences"
          icon={Shield}
        >
          <div className="space-y-4">
            <div>
              <h4 className="font-medium text-gray-900 mb-3">Change Password</h4>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div>
                  <label className="form-label">Current Password</label>
                  <div className="relative">
                    <input
                      type={showPassword ? 'text' : 'password'}
                      className="input pr-10"
                      placeholder="Enter current password"
                    />
                    <button
                      type="button"
                      className="absolute inset-y-0 right-0 pr-3 flex items-center"
                      onClick={() => setShowPassword(!showPassword)}
                    >
                      {showPassword ? (
                        <EyeOff className="h-4 w-4 text-gray-400" />
                      ) : (
                        <Eye className="h-4 w-4 text-gray-400" />
                      )}
                    </button>
                  </div>
                </div>
                <div>
                  <label className="form-label">New Password</label>
                  <input
                    type="password"
                    className="input"
                    placeholder="Enter new password"
                  />
                </div>
              </div>
              <div className="mt-4">
                <button onClick={handleChangePassword} className="btn btn-primary btn-md">
                  Update Password
                </button>
              </div>
            </div>

            <div className="border-t pt-4">
              <h4 className="font-medium text-gray-900 mb-3">Two-Factor Authentication</h4>
              <div className="flex justify-between items-center">
                <div>
                  <p className="text-sm text-gray-600">
                    Add an extra layer of security to your account
                  </p>
                </div>
                <button className="btn btn-outline btn-md">
                  Enable 2FA
                </button>
              </div>
            </div>
          </div>
        </SettingsSection>

        {/* Notification Settings */}
        <SettingsSection
          title="Notifications"
          description="Choose how you want to be notified about updates"
          icon={Bell}
        >
          <div className="space-y-4">
            {Object.entries({
              email: 'Email Notifications',
              push: 'Push Notifications',
              sms: 'SMS Notifications',
              marketing: 'Marketing Communications'
            }).map(([key, label]) => (
              <div key={key} className="flex items-center justify-between">
                <div>
                  <h4 className="font-medium text-gray-900">{label}</h4>
                  <p className="text-sm text-gray-600">
                    {key === 'email' && 'Receive updates via email'}
                    {key === 'push' && 'Browser push notifications'}
                    {key === 'sms' && 'Text message alerts'}
                    {key === 'marketing' && 'Product updates and promotions'}
                  </p>
                </div>
                <label className="relative inline-flex items-center cursor-pointer">
                  <input
                    type="checkbox"
                    className="sr-only peer"
                    checked={notifications[key as keyof typeof notifications]}
                    onChange={() => handleNotificationChange(key as keyof typeof notifications)}
                  />
                  <div className="w-11 h-6 bg-gray-200 peer-focus:outline-none peer-focus:ring-4 peer-focus:ring-primary/20 rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-primary"></div>
                </label>
              </div>
            ))}
          </div>
        </SettingsSection>

        {/* Data Management */}
        <SettingsSection
          title="Data Management"
          description="Export your data or delete your account"
          icon={Upload}
        >
          <div className="space-y-4">
            <div className="flex justify-between items-center">
              <div>
                <h4 className="font-medium text-gray-900">Export Data</h4>
                <p className="text-sm text-gray-600">
                  Download a copy of your account data
                </p>
              </div>
              <button onClick={handleExportData} className="btn btn-outline btn-md">
                <Download className="h-4 w-4 mr-2" />
                Export
              </button>
            </div>

            <div className="border-t pt-4">
              <div className="flex justify-between items-center">
                <div>
                  <h4 className="font-medium text-red-600">Delete Account</h4>
                  <p className="text-sm text-gray-600">
                    Permanently delete your account and all data
                  </p>
                </div>
                <button 
                  onClick={handleDeleteAccount}
                  className="btn bg-red-600 text-white hover:bg-red-700 btn-md"
                >
                  <Trash2 className="h-4 w-4 mr-2" />
                  Delete Account
                </button>
              </div>
            </div>
          </div>
        </SettingsSection>
      </div>
    </div>
  );
}