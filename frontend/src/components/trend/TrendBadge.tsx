'use client';

import { useTrendLabelStyle } from '@/hooks/useTrendAnalysis';

interface TrendBadgeProps {
  label: string;
  score?: number;
  size?: 'sm' | 'md' | 'lg';
  showScore?: boolean;
  className?: string;
}

export function TrendBadge({ 
  label, 
  score, 
  size = 'md', 
  showScore = false, 
  className = '' 
}: TrendBadgeProps) {
  const { getTrendLabelStyle, getTrendScoreColor } = useTrendLabelStyle();
  const style = getTrendLabelStyle(label);

  const sizeClasses = {
    sm: 'px-2 py-0.5 text-xs',
    md: 'px-2.5 py-0.5 text-xs',
    lg: 'px-3 py-1 text-sm'
  };

  return (
    <span className={`
      inline-flex items-center rounded-full font-medium border
      ${style.className}
      ${sizeClasses[size]}
      ${className}
    `}>
      <span className="mr-1">{style.icon}</span>
      {label}
      {showScore && score !== undefined && (
        <span className={`ml-1 font-semibold ${getTrendScoreColor(score)}`}>
          {score}
        </span>
      )}
    </span>
  );
}

interface TrendScoreProps {
  score: number;
  label?: string;
  size?: 'sm' | 'md' | 'lg';
  showLabel?: boolean;
  className?: string;
}

export function TrendScore({ 
  score, 
  label, 
  size = 'md', 
  showLabel = true, 
  className = '' 
}: TrendScoreProps) {
  const { getTrendScoreColor } = useTrendLabelStyle();

  const sizeClasses = {
    sm: 'text-sm',
    md: 'text-base',
    lg: 'text-lg'
  };

  return (
    <div className={`flex items-center space-x-2 ${className}`}>
      <span className={`font-semibold ${getTrendScoreColor(score)} ${sizeClasses[size]}`}>
        {score.toFixed(1)}
      </span>
      {showLabel && label && (
        <TrendBadge label={label} size={size === 'lg' ? 'md' : 'sm'} />
      )}
    </div>
  );
}

interface TrendIndicatorProps {
  googleTrend: number;
  socialScore: number;
  finalScore: number;
  label: string;
  compact?: boolean;
  className?: string;
}

export function TrendIndicator({ 
  googleTrend, 
  socialScore, 
  finalScore, 
  label, 
  compact = false, 
  className = '' 
}: TrendIndicatorProps) {
  const { getTrendScoreColor } = useTrendLabelStyle();

  if (compact) {
    return (
      <div className={`flex items-center space-x-2 ${className}`}>
        <TrendBadge label={label} size="sm" />
        <span className={`text-sm font-medium ${getTrendScoreColor(finalScore)}`}>
          {finalScore.toFixed(1)}
        </span>
      </div>
    );
  }

  return (
    <div className={`space-y-2 ${className}`}>
      <div className="flex items-center justify-between">
        <TrendBadge label={label} />
        <span className={`text-lg font-semibold ${getTrendScoreColor(finalScore)}`}>
          {finalScore.toFixed(1)}
        </span>
      </div>
      <div className="grid grid-cols-2 gap-2 text-sm">
        <div className="flex justify-between">
          <span className="text-gray-600">Google:</span>
          <span className="font-medium">{googleTrend.toFixed(1)}</span>
        </div>
        <div className="flex justify-between">
          <span className="text-gray-600">Social:</span>
          <span className="font-medium">{socialScore.toFixed(1)}</span>
        </div>
      </div>
    </div>
  );
}