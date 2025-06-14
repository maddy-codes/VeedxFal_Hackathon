'use client';

import React, { useState, useEffect } from 'react';
import { AvatarVideo } from '@/types';

interface AutoAvatarBriefingProps {
  shopId: number;
}

const AutoAvatarBriefing: React.FC<AutoAvatarBriefingProps> = ({ shopId }) => {
  const [avatarVideo, setAvatarVideo] = useState<AvatarVideo | null>(null);
  const [isGenerating, setIsGenerating] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [isProcessing, setIsProcessing] = useState(false);
  const [requestId, setRequestId] = useState<string | null>(null);
  const [addSubtitles, setAddSubtitles] = useState(false);

  // Auto-generate avatar video when component mounts
  useEffect(() => {
    generateAvatarVideo();
  }, [shopId]);

  const generateAvatarVideo = async () => {
    setIsGenerating(true);
    setError(null);
    setAvatarVideo(null);

    try {
      const params = new URLSearchParams({
        shop_id: shopId.toString(),
        avatar_id: 'marcus_primary', // Fixed to Jaz/Marcus avatar
        include_business_context: 'true',
        add_subtitles: addSubtitles.toString()
      });

      const response = await fetch(`http://localhost:8000/api/v1/video/avatar/generate?${params}`, {
        method: 'POST',
      });

      if (response.ok) {
        const data: { data: any } = await response.json();
        
        // Check if video is still processing
        if (data.data.processing || data.data.status === 'processing') {
          setIsProcessing(true);
          setRequestId(data.data.request_id);
          setIsGenerating(false);
          
          // Start polling for completion
          pollForCompletion(data.data.request_id);
        } else {
          setAvatarVideo(data.data);
        }
      } else {
        const errorData = await response.json();
        setError(errorData.detail || 'Failed to generate avatar briefing');
      }
    } catch (err) {
      setError('Error generating avatar briefing');
      console.error('Error generating avatar briefing:', err);
    } finally {
      setIsGenerating(false);
    }
  };

  const pollForCompletion = async (requestId: string) => {
    const maxAttempts = 60; // Poll for up to 5 minutes (60 * 5 seconds)
    let attempts = 0;

    const poll = async () => {
      try {
        const response = await fetch(`http://localhost:8000/api/v1/video/avatar/status/${requestId}`);
        
        if (response.ok) {
          const data = await response.json();
          
          if (data.status === 'completed' && data.video_url) {
            // Video is ready
            setAvatarVideo({
              video_url: data.video_url,
              duration_seconds: data.duration_seconds || 45,
              format: data.format || 'mp4',
              resolution: '1080p',
              generated_at: new Date().toISOString(),
              script_content: 'Your personalized business briefing is ready!',
              avatar_id: 'marcus_primary',
              ai_provider: 'fal_ai',
              model: 'veed/avatars/text-to-video',
              status: 'completed',
              mock_response: false
            });
            setIsProcessing(false);
            setRequestId(null);
            return;
          }
        }
        
        attempts++;
        if (attempts < maxAttempts) {
          // Continue polling every 5 seconds
          setTimeout(poll, 5000);
        } else {
          // Timeout - show error
          setError('Video generation timed out. Please try again.');
          setIsProcessing(false);
          setRequestId(null);
        }
      } catch (err) {
        console.error('Polling error:', err);
        attempts++;
        if (attempts < maxAttempts) {
          setTimeout(poll, 5000);
        } else {
          setError('Failed to check video status. Please try again.');
          setIsProcessing(false);
          setRequestId(null);
        }
      }
    };

    // Start polling
    setTimeout(poll, 5000); // First check after 5 seconds
  };

  if (isGenerating || isProcessing) {
    return (
      <div className="bg-white rounded-lg shadow-md p-6">
        <div className="text-center">
          <div className="flex items-center justify-center mb-4">
            <div className="w-16 h-16 bg-gradient-to-br from-blue-400 to-purple-500 rounded-full flex items-center justify-center text-white font-bold text-xl">
              J
            </div>
          </div>
          <h3 className="text-lg font-semibold text-gray-900 mb-2">
            {isProcessing ? 'Creating Your Video Briefing' : 'Generating Your Business Briefing'}
          </h3>
          <p className="text-gray-600 mb-4">
            {isProcessing
              ? 'Jaz is creating your personalized video briefing. This may take a few minutes...'
              : 'Jaz is analyzing your store data and preparing your personalized briefing...'
            }
          </p>
          <div className="flex items-center justify-center space-x-2">
            <svg className="animate-spin h-5 w-5 text-blue-600" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
              <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
              <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
            </svg>
            <span className="text-blue-600 font-medium">
              {isProcessing ? 'Creating Video...' : 'Processing...'}
            </span>
          </div>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="bg-white rounded-lg shadow-md p-6">
        <div className="text-center">
          <div className="flex items-center justify-center mb-4">
            <div className="w-16 h-16 bg-red-100 rounded-full flex items-center justify-center">
              <svg className="w-8 h-8 text-red-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-2.5L13.732 4c-.77-.833-1.964-.833-2.732 0L3.732 16.5c-.77.833.192 2.5 1.732 2.5z" />
              </svg>
            </div>
          </div>
          <h3 className="text-lg font-semibold text-gray-900 mb-2">
            Briefing Generation Failed
          </h3>
          <p className="text-gray-600 mb-4">{error}</p>
          <button
            onClick={generateAvatarVideo}
            className="bg-blue-600 text-white px-4 py-2 rounded-md hover:bg-blue-700 transition-colors"
          >
            Try Again
          </button>
        </div>
      </div>
    );
  }

  if (!avatarVideo) {
    return (
      <div className="bg-white rounded-lg shadow-md p-6">
        <div className="text-center">
          <h3 className="text-lg font-semibold text-gray-900 mb-2">
            AI Business Briefing
          </h3>
          <p className="text-gray-600">Loading your personalized briefing...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="bg-white rounded-lg shadow-md overflow-hidden">
      {/* Header */}
      <div className="bg-gradient-to-r from-blue-600 to-purple-600 text-white p-4">
        <div className="flex items-center space-x-3">
          <div className="w-12 h-12 bg-white bg-opacity-20 rounded-full flex items-center justify-center text-white font-bold">
            J
          </div>
          <div>
            <h3 className="text-lg font-semibold">Your Business Briefing</h3>
            <p className="text-blue-100 text-sm">with Jaz, Analyst at BizPredict</p>
          </div>
        </div>
      </div>

      {/* Video Player */}
      <div className="bg-black aspect-video">
        <video
          controls
          className="w-full h-full object-cover"
          poster="/api/placeholder/640/360"
          autoPlay={false}
        >
          <source src={avatarVideo.video_url} type="video/mp4" />
          Your browser does not support the video tag.
        </video>
      </div>

      {/* Video Details */}
      <div className="p-4">
        <div className="flex items-center justify-between mb-3">
          <div className="flex items-center space-x-2">
            <span className="text-sm font-medium text-gray-900">Duration:</span>
            <span className="text-sm text-gray-600">{avatarVideo.duration_seconds}s</span>
          </div>
          <div className="flex items-center space-x-2">
            <span className="text-sm font-medium text-gray-900">Generated:</span>
            <span className="text-sm text-gray-600">
              {new Date(avatarVideo.generated_at).toLocaleTimeString()}
            </span>
          </div>
        </div>

        {/* Script Preview */}
        <div className="mb-4">
          <h4 className="text-sm font-medium text-gray-900 mb-2">Briefing Summary:</h4>
          <p className="text-sm text-gray-600 bg-gray-50 p-3 rounded">
            {avatarVideo.script_content.substring(0, 150)}...
          </p>
        </div>

        {/* Mock Response Warning */}
        {avatarVideo.mock_response && (
          <div className="mb-4 p-3 bg-yellow-50 border border-yellow-200 rounded">
            <p className="text-sm text-yellow-800">
              ⚠️ Demo Mode: {avatarVideo.message}
            </p>
          </div>
        )}

        {/* Subtitle Options */}
        <div className="mb-4 p-3 bg-gray-50 rounded-md">
          <label className="flex items-center space-x-2">
            <input
              type="checkbox"
              checked={addSubtitles}
              onChange={(e) => setAddSubtitles(e.target.checked)}
              className="rounded border-gray-300 text-blue-600 focus:ring-blue-500"
            />
            <span className="text-sm font-medium text-gray-700">
              Add Subtitles (ZapCap)
            </span>
          </label>
          <p className="text-xs text-gray-500 mt-1">
            Automatically generate and add subtitles to your video briefing
          </p>
        </div>

        {/* Subtitle Status */}
        {avatarVideo?.subtitles_added !== undefined && (
          <div className="mb-4 p-3 rounded-md">
            {avatarVideo.subtitles_added ? (
              <div className="flex items-center text-green-700 bg-green-50 p-2 rounded">
                <span className="text-sm">✅ Subtitles added successfully</span>
              </div>
            ) : (
              <div className="flex items-center text-yellow-700 bg-yellow-50 p-2 rounded">
                <span className="text-sm">⚠️ Subtitles not added: {avatarVideo.subtitle_error || 'Feature not enabled'}</span>
              </div>
            )}
          </div>
        )}

        {/* Action Buttons */}
        <div className="flex space-x-3">
          <button
            onClick={generateAvatarVideo}
            className="flex-1 bg-blue-600 text-white py-2 px-4 rounded-md text-sm font-medium hover:bg-blue-700 transition-colors"
          >
            🔄 Generate New Briefing
          </button>
          <a
            href={avatarVideo.video_url}
            download={`business-briefing-${new Date().toISOString().split('T')[0]}.mp4`}
            className="flex-1 bg-gray-600 text-white text-center py-2 px-4 rounded-md text-sm font-medium hover:bg-gray-700 transition-colors"
          >
            📥 Download
          </a>
        </div>
      </div>
    </div>
  );
};

export default AutoAvatarBriefing;