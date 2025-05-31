'use client';

import { useState } from 'react';
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { z } from 'zod';
import { Calculator, DollarSign, Percent } from 'lucide-react';

// Validation schema
const pricingSchema = z.object({
  costPrice: z.number().min(0.01, 'Cost price must be greater than 0'),
  markupPercentage: z.number().min(0, 'Markup percentage must be 0 or greater'),
});

type PricingFormData = z.infer<typeof pricingSchema>;

export default function PricingCalculatorPage() {
  const [recommendedPrice, setRecommendedPrice] = useState<number>(0);
  const [isCalculated, setIsCalculated] = useState(false);

  const {
    register,
    handleSubmit,
    watch,
    formState: { errors },
    reset,
  } = useForm<PricingFormData>({
    resolver: zodResolver(pricingSchema),
    defaultValues: {
      costPrice: 0,
      markupPercentage: 0,
    },
  });

  const watchedValues = watch();

  const calculatePrice = (data: PricingFormData) => {
    const { costPrice, markupPercentage } = data;
    const calculatedPrice = costPrice * (1 + markupPercentage / 100);
    setRecommendedPrice(calculatedPrice);
    setIsCalculated(true);
  };

  const handleReset = () => {
    reset();
    setRecommendedPrice(0);
    setIsCalculated(false);
  };

  const formatCurrency = (amount: number): string => {
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: 'USD',
    }).format(amount);
  };

  // Real-time calculation as user types
  const getRealTimePrice = (): number => {
    if (watchedValues.costPrice > 0 && watchedValues.markupPercentage >= 0) {
      return watchedValues.costPrice * (1 + watchedValues.markupPercentage / 100);
    }
    return 0;
  };

  return (
    <div className="min-h-screen bg-accent-100 py-8">
      <div className="max-w-2xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="text-center mb-8">
          <h1 className="text-3xl font-bold text-gray-900 mb-2">Cost-Plus Pricing Calculator</h1>
          <p className="text-gray-600">Calculate optimal pricing based on cost and desired markup</p>
        </div>

        <div className="bg-white rounded-lg shadow-lg p-8">
          <div className="flex items-center justify-center mb-6">
            <div className="bg-primary/10 p-3 rounded-full">
              <Calculator className="h-8 w-8 text-primary" />
            </div>
          </div>

          <form onSubmit={handleSubmit(calculatePrice)} className="space-y-6">
            {/* Cost Price Input */}
            <div className="form-group">
              <label htmlFor="costPrice" className="form-label text-lg font-medium">
                Cost Price
              </label>
              <div className="relative">
                <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
                  <DollarSign className="h-5 w-5 text-gray-400" />
                </div>
                <input
                  {...register('costPrice', { valueAsNumber: true })}
                  type="number"
                  step="0.01"
                  min="0"
                  id="costPrice"
                  className="input pl-10 text-lg"
                  placeholder="0.00"
                />
              </div>
              {errors.costPrice && (
                <p className="form-error">{errors.costPrice.message}</p>
              )}
            </div>

            {/* Markup Percentage Input */}
            <div className="form-group">
              <label htmlFor="markupPercentage" className="form-label text-lg font-medium">
                Markup Percentage
              </label>
              <div className="relative">
                <div className="absolute inset-y-0 right-0 pr-3 flex items-center pointer-events-none">
                  <Percent className="h-5 w-5 text-gray-400" />
                </div>
                <input
                  {...register('markupPercentage', { valueAsNumber: true })}
                  type="number"
                  step="0.1"
                  min="0"
                  id="markupPercentage"
                  className="input pr-10 text-lg"
                  placeholder="0.0"
                />
              </div>
              {errors.markupPercentage && (
                <p className="form-error">{errors.markupPercentage.message}</p>
              )}
            </div>

            {/* Recommended Price Display */}
            <div className="bg-gray-50 rounded-lg p-6 text-center">
              <label className="block text-lg font-medium text-gray-700 mb-2">
                Recommended Price
              </label>
              <div className="text-4xl font-bold text-primary">
                {formatCurrency(getRealTimePrice())}
              </div>
              {getRealTimePrice() > 0 && (
                <div className="mt-2 text-sm text-gray-600">
                  Markup: {formatCurrency(getRealTimePrice() - (watchedValues.costPrice || 0))}
                </div>
              )}
            </div>

            {/* Action Buttons */}
            <div className="flex space-x-4">
              <button
                type="submit"
                className="btn btn-primary btn-lg flex-1"
                disabled={!watchedValues.costPrice || watchedValues.costPrice <= 0}
              >
                Calculate
              </button>
              <button
                type="button"
                onClick={handleReset}
                className="btn btn-outline btn-lg px-8"
              >
                Reset
              </button>
            </div>
          </form>

          {/* Calculation Breakdown */}
          {getRealTimePrice() > 0 && (
            <div className="mt-8 border-t pt-6">
              <h3 className="text-lg font-medium text-gray-900 mb-4">Calculation Breakdown</h3>
              <div className="space-y-3">
                <div className="flex justify-between items-center">
                  <span className="text-gray-600">Cost Price:</span>
                  <span className="font-medium">{formatCurrency(watchedValues.costPrice || 0)}</span>
                </div>
                <div className="flex justify-between items-center">
                  <span className="text-gray-600">Markup ({watchedValues.markupPercentage || 0}%):</span>
                  <span className="font-medium">
                    {formatCurrency((watchedValues.costPrice || 0) * (watchedValues.markupPercentage || 0) / 100)}
                  </span>
                </div>
                <div className="border-t pt-2">
                  <div className="flex justify-between items-center">
                    <span className="text-lg font-medium text-gray-900">Selling Price:</span>
                    <span className="text-lg font-bold text-primary">
                      {formatCurrency(getRealTimePrice())}
                    </span>
                  </div>
                </div>
                <div className="flex justify-between items-center text-sm text-gray-600">
                  <span>Profit Margin:</span>
                  <span>
                    {watchedValues.costPrice > 0 
                      ? `${((getRealTimePrice() - watchedValues.costPrice) / getRealTimePrice() * 100).toFixed(1)}%`
                      : '0%'
                    }
                  </span>
                </div>
              </div>
            </div>
          )}

          {/* Pricing Tips */}
          <div className="mt-8 bg-blue-50 rounded-lg p-6">
            <h3 className="text-lg font-medium text-blue-900 mb-3">Pricing Tips</h3>
            <ul className="space-y-2 text-sm text-blue-800">
              <li className="flex items-start">
                <span className="w-2 h-2 bg-blue-500 rounded-full mt-2 mr-3 flex-shrink-0"></span>
                Consider market competition when setting your markup percentage
              </li>
              <li className="flex items-start">
                <span className="w-2 h-2 bg-blue-500 rounded-full mt-2 mr-3 flex-shrink-0"></span>
                Factor in all costs including shipping, handling, and overhead
              </li>
              <li className="flex items-start">
                <span className="w-2 h-2 bg-blue-500 rounded-full mt-2 mr-3 flex-shrink-0"></span>
                Test different price points to find the optimal balance
              </li>
              <li className="flex items-start">
                <span className="w-2 h-2 bg-blue-500 rounded-full mt-2 mr-3 flex-shrink-0"></span>
                Monitor customer response and adjust pricing accordingly
              </li>
            </ul>
          </div>
        </div>
      </div>
    </div>
  );
}