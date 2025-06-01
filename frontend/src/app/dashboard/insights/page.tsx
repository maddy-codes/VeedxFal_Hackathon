'use client';

import { useState, useEffect } from 'react';
import { useApp, useProductFilter } from '@/contexts/AppContext';
import { Play, Pause, Volume2, Maximize } from 'lucide-react';
import { TrendAnalysisCard } from '@/components/trend/TrendAnalysisCard';
import { TrendBadge, TrendIndicator } from '@/components/trend/TrendBadge';
import { BusinessContextCard } from '@/components/business/BusinessContextCard';

interface VideoPlayerProps {
  src?: string;
  title?: string;
}

function VideoPlayer({ src, title = "AI Advisor Video" }: VideoPlayerProps) {
  const [isPlaying, setIsPlaying] = useState(false);
  const [currentTime, setCurrentTime] = useState(0);
  const [duration, setDuration] = useState(0);

  const togglePlay = () => {
    setIsPlaying(!isPlaying);
  };

  const formatTime = (time: number) => {
    const minutes = Math.floor(time / 60);
    const seconds = Math.floor(time % 60);
    return `${minutes}:${seconds.toString().padStart(2, '0')}`;
  };

  return (
    <div className="bg-white rounded-lg shadow-lg overflow-hidden">
      <div className="relative bg-gray-900 aspect-video">
        {/* Video placeholder */}
        <div className="absolute inset-0 flex items-center justify-center">
          <div className="text-center text-white">
            <div className="w-16 h-16 bg-primary rounded-full flex items-center justify-center mx-auto mb-4">
              <Play className="h-8 w-8 text-white ml-1" />
            </div>
            <p className="text-lg font-medium">{title}</p>
            <p className="text-sm text-gray-300">Click to play AI advisor insights</p>
          </div>
        </div>

        {/* Play button overlay */}
        <button
          onClick={togglePlay}
          className="absolute inset-0 flex items-center justify-center bg-black bg-opacity-30 hover:bg-opacity-40 transition-all"
        >
          <div className="w-20 h-20 bg-white bg-opacity-90 rounded-full flex items-center justify-center">
            {isPlaying ? (
              <Pause className="h-10 w-10 text-gray-900" />
            ) : (
              <Play className="h-10 w-10 text-gray-900 ml-1" />
            )}
          </div>
        </button>
      </div>

      {/* Video controls */}
      <div className="bg-gray-800 text-white p-4">
        <div className="flex items-center justify-between mb-2">
          <div className="flex items-center space-x-4">
            <button
              onClick={togglePlay}
              className="flex items-center justify-center w-8 h-8 bg-primary rounded hover:bg-primary/80 transition-colors"
            >
              {isPlaying ? (
                <Pause className="h-4 w-4" />
              ) : (
                <Play className="h-4 w-4 ml-0.5" />
              )}
            </button>
            
            <div className="flex items-center space-x-2">
              <Volume2 className="h-4 w-4" />
              <div className="w-16 h-1 bg-gray-600 rounded">
                <div className="w-3/4 h-full bg-white rounded"></div>
              </div>
            </div>
          </div>

          <div className="flex items-center space-x-4">
            <span className="text-sm">
              {formatTime(currentTime)} / {formatTime(duration || 180)}
            </span>
            <button className="hover:text-primary transition-colors">
              <Maximize className="h-4 w-4" />
            </button>
          </div>
        </div>

        {/* Progress bar */}
        <div className="w-full h-1 bg-gray-600 rounded cursor-pointer">
          <div 
            className="h-full bg-primary rounded transition-all"
            style={{ width: `${(currentTime / (duration || 180)) * 100}%` }}
          ></div>
        </div>
      </div>
    </div>
  );
}

interface FilterTabProps {
  label: string;
  isActive: boolean;
  onClick: () => void;
  count?: number;
}

function FilterTab({ label, isActive, onClick, count }: FilterTabProps) {
  return (
    <button
      onClick={onClick}
      className={`
        px-4 py-2 text-sm font-medium rounded-md transition-colors
        ${isActive 
          ? 'bg-primary text-white' 
          : 'text-gray-600 hover:text-primary hover:bg-gray-100'
        }
      `}
    >
      {label}
      {count !== undefined && (
        <span className={`ml-2 px-2 py-0.5 text-xs rounded-full ${
          isActive ? 'bg-white text-primary' : 'bg-gray-200 text-gray-600'
        }`}>
          {count}
        </span>
      )}
    </button>
  );
}

export default function ProductInsightsPage() {
  const { products, setProducts } = useApp();
  const { selectedFilter, setSelectedFilter, filterOptions } = useProductFilter();

  // Sample data matching the mockup exactly
  const sampleProducts = [
    {
      sku_id: 1,
      shop_id: 1,
      sku_code: 'WE001',
      product_title: 'Wireless Earbuds',
      current_price: 49.99,
      inventory_level: 25,
      cost_price: 30.00,
      status: 'active',
      created_at: new Date().toISOString(),
      updated_at: new Date().toISOString(),
      recommended_price: 59.99,
      recommendation_type: 'underpriced',
      pricing_reason: 'Increase price to $59.99',
      confidence_score: 0.85,
      trend_label: 'Stable',
    },
    {
      sku_id: 2,
      shop_id: 1,
      sku_code: 'CS001',
      product_title: 'Classic Sneaker',
      current_price: 89.99,
      inventory_level: 75,
      cost_price: 45.00,
      status: 'active',
      created_at: new Date().toISOString(),
      updated_at: new Date().toISOString(),
      recommendation_type: 'overstocked',
      pricing_reason: 'Run a clearance sale',
      confidence_score: 0.75,
      trend_label: 'Declining',
    },
    {
      sku_id: 3,
      shop_id: 1,
      sku_code: 'DJ001',
      product_title: 'Denim Jacket',
      current_price: 79.99,
      inventory_level: 15,
      cost_price: 40.00,
      status: 'active',
      created_at: new Date().toISOString(),
      updated_at: new Date().toISOString(),
      trend_label: 'Hot',
      trend_score: 85,
      pricing_reason: 'Trending upward',
      confidence_score: 0.90,
    },
    {
      sku_id: 4,
      shop_id: 1,
      sku_code: 'SW001',
      product_title: 'Smartwatch',
      current_price: 199.99,
      inventory_level: 8,
      cost_price: 120.00,
      status: 'active',
      created_at: new Date().toISOString(),
      updated_at: new Date().toISOString(),
      trend_label: 'Hot',
      trend_score: 92,
      pricing_reason: 'High demand currently',
      confidence_score: 0.95,
    },
  ];

  useEffect(() => {
    setProducts(sampleProducts);
  }, []); // Remove setProducts from dependency array to prevent infinite loop

  const getRecommendationDisplay = (product: any) => {
    if (product.recommendation_type === 'underpriced') {
      return `Underpriced - ${product.pricing_reason}`;
    }
    if (product.recommendation_type === 'overstocked') {
      return `Overstocked - ${product.pricing_reason}`;
    }
    if (product.trend_label === 'Hot') {
      return `Hot - ${product.pricing_reason}`;
    }
    return product.pricing_reason || 'No specific recommendation';
  };

  const getFilteredProducts = () => {
    if (selectedFilter === 'All') return sampleProducts;
    
    return sampleProducts.filter(product => {
      switch (selectedFilter) {
        case 'Underpriced':
          return product.recommendation_type === 'underpriced';
        case 'Overstocked':
          return product.recommendation_type === 'overstocked';
        case 'Hot':
          return product.trend_label === 'Hot';
        default:
          return true;
      }
    });
  };

  const filteredProducts = getFilteredProducts();

  return (
    <div className="space-y-8">
      {/* Product Insights Section */}
      <div>
        <h2 className="text-2xl font-bold text-gray-900 mb-6">Product Insights</h2>
        
        {/* Business Context Card - AI-powered business summary */}
        <div className="mb-8">
          <BusinessContextCard shopId={1} />
        </div>

        {/* Video Player */}
        <div className="mb-8">
          <VideoPlayer title="AI Retail Advisor - Product Insights" />
        </div>

        {/* Trend Analysis Card */}
        <div className="mb-8">
          <TrendAnalysisCard shopId={1} />
        </div>

        {/* Filter Tabs */}
        <div className="flex space-x-2 mb-6">
          {filterOptions.map((filter) => (
            <FilterTab
              key={filter}
              label={filter}
              isActive={selectedFilter === filter}
              onClick={() => setSelectedFilter(filter)}
            />
          ))}
        </div>

        {/* Product Recommendations Table */}
        <div className="bg-white rounded-lg shadow overflow-hidden">
          <div className="px-6 py-4 border-b border-gray-200">
            <h3 className="text-lg font-medium text-gray-900">Product Recommendations</h3>
          </div>
          
          <div className="overflow-x-auto">
            <table className="min-w-full divide-y divide-gray-200">
              <thead className="bg-gray-50">
                <tr>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Product
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Trend
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Recommendation
                  </th>
                </tr>
              </thead>
              <tbody className="bg-white divide-y divide-gray-200">
                {filteredProducts.map((product) => (
                  <tr key={product.sku_id} className="hover:bg-gray-50">
                    <td className="px-6 py-4 whitespace-nowrap">
                      <div className="flex items-center">
                        <div className="flex-shrink-0 h-12 w-12">
                          <div className="h-12 w-12 bg-gray-200 rounded-lg flex items-center justify-center">
                            <span className="text-gray-500 text-xs font-medium">
                              {product.product_title.split(' ').map(w => w[0]).join('').slice(0, 2)}
                            </span>
                          </div>
                        </div>
                        <div className="ml-4">
                          <div className="text-sm font-medium text-gray-900">
                            {product.product_title}
                          </div>
                          <div className="text-sm text-gray-500">
                            SKU: {product.sku_code} • ${product.current_price.toFixed(2)}
                          </div>
                        </div>
                      </div>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      {product.trend_label && (
                        <div className="space-y-1">
                          <TrendBadge label={product.trend_label} size="sm" />
                          {product.trend_score && (
                            <div className="text-xs text-gray-500">
                              Score: {product.trend_score}
                            </div>
                          )}
                        </div>
                      )}
                    </td>
                    <td className="px-6 py-4">
                      <div className="text-sm text-gray-900">
                        {getRecommendationDisplay(product)}
                      </div>
                      {product.confidence_score && (
                        <div className="text-xs text-gray-500 mt-1">
                          Confidence: {(product.confidence_score * 100).toFixed(0)}%
                        </div>
                      )}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>

          {filteredProducts.length === 0 && (
            <div className="text-center py-12">
              <p className="text-gray-500">No products found for the selected filter.</p>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}