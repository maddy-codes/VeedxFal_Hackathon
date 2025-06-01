'use client';

import React, { useState } from 'react';
import { MessageCircle, Play, User, Sparkles, TrendingUp, BarChart3 } from 'lucide-react';
import AutoAvatarBriefing from './AutoAvatarBriefing';

interface AIBusinessManagerProps {
  shopId: number;
}

const AIBusinessManager: React.FC<AIBusinessManagerProps> = ({ shopId }) => {
  const [showBriefing, setShowBriefing] = useState(false);

  return (
    <div className="bg-white rounded-lg shadow-md overflow-hidden">
      {!showBriefing ? (
        // Initial state - Call to action
        <div className="p-8">
          {/* Header */}
          <div className="text-center mb-8">
            <div className="w-20 h-20 bg-gradient-to-br from-blue-500 to-purple-600 rounded-full flex items-center justify-center mx-auto mb-4">
              <User className="w-10 h-10 text-white" />
            </div>
            <h2 className="text-2xl font-bold text-gray-900 mb-2">
              Meet Jaz, Your AI Business Manager
            </h2>
            <p className="text-gray-600 max-w-md mx-auto">
              Get personalized video briefings with key insights, performance updates, and strategic recommendations for your business.
            </p>
          </div>

          {/* Features */}
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
            <div className="text-center">
              <div className="w-12 h-12 bg-blue-100 rounded-lg flex items-center justify-center mx-auto mb-3">
                <TrendingUp className="w-6 h-6 text-blue-600" />
              </div>
              <h3 className="font-semibold text-gray-900 mb-1">Real-time Analysis</h3>
              <p className="text-sm text-gray-600">
                Live insights from your store performance and market trends
              </p>
            </div>
            
            <div className="text-center">
              <div className="w-12 h-12 bg-purple-100 rounded-lg flex items-center justify-center mx-auto mb-3">
                <Sparkles className="w-6 h-6 text-purple-600" />
              </div>
              <h3 className="font-semibold text-gray-900 mb-1">AI-Powered Insights</h3>
              <p className="text-sm text-gray-600">
                Advanced analytics and personalized recommendations
              </p>
            </div>
            
            <div className="text-center">
              <div className="w-12 h-12 bg-green-100 rounded-lg flex items-center justify-center mx-auto mb-3">
                <BarChart3 className="w-6 h-6 text-green-600" />
              </div>
              <h3 className="font-semibold text-gray-900 mb-1">Strategic Guidance</h3>
              <p className="text-sm text-gray-600">
                Actionable advice to optimize your business performance
              </p>
            </div>
          </div>

          {/* Call to Action */}
          <div className="text-center">
            <button
              onClick={() => setShowBriefing(true)}
              className="inline-flex items-center px-8 py-4 bg-gradient-to-r from-blue-600 to-purple-600 text-white font-semibold rounded-lg hover:from-blue-700 hover:to-purple-700 transition-all duration-200 shadow-lg hover:shadow-xl transform hover:scale-105"
            >
              <MessageCircle className="w-5 h-5 mr-3" />
              Speak with Your AI Business Manager
            </button>
            <p className="text-sm text-gray-500 mt-3">
              Get your personalized video briefing in under 2 minutes
            </p>
          </div>

          {/* Sample Topics */}
          <div className="mt-8 p-6 bg-gray-50 rounded-lg">
            <h3 className="font-semibold text-gray-900 mb-3">What Jaz will cover in your briefing:</h3>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
              <div className="flex items-center text-sm text-gray-700">
                <div className="w-2 h-2 bg-blue-500 rounded-full mr-3"></div>
                Revenue performance and trends
              </div>
              <div className="flex items-center text-sm text-gray-700">
                <div className="w-2 h-2 bg-green-500 rounded-full mr-3"></div>
                Top performing products
              </div>
              <div className="flex items-center text-sm text-gray-700">
                <div className="w-2 h-2 bg-purple-500 rounded-full mr-3"></div>
                Market trend analysis
              </div>
              <div className="flex items-center text-sm text-gray-700">
                <div className="w-2 h-2 bg-orange-500 rounded-full mr-3"></div>
                Strategic recommendations
              </div>
              <div className="flex items-center text-sm text-gray-700">
                <div className="w-2 h-2 bg-red-500 rounded-full mr-3"></div>
                Inventory insights
              </div>
              <div className="flex items-center text-sm text-gray-700">
                <div className="w-2 h-2 bg-indigo-500 rounded-full mr-3"></div>
                Growth opportunities
              </div>
            </div>
          </div>
        </div>
      ) : (
        // Briefing state
        <div className="p-6">
          <div className="flex items-center justify-between mb-6">
            <div className="flex items-center space-x-3">
              <div className="w-10 h-10 bg-gradient-to-br from-blue-500 to-purple-600 rounded-full flex items-center justify-center">
                <User className="w-5 h-5 text-white" />
              </div>
              <div>
                <h3 className="text-lg font-semibold text-gray-900">AI Business Manager</h3>
                <p className="text-sm text-gray-600">Personalized briefing for your store</p>
              </div>
            </div>
            <button
              onClick={() => setShowBriefing(false)}
              className="text-gray-400 hover:text-gray-600 transition-colors"
            >
              <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
              </svg>
            </button>
          </div>
          
          <AutoAvatarBriefing shopId={shopId} />
        </div>
      )}
    </div>
  );
};

export default AIBusinessManager;