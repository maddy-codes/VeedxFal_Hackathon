'use client';

import React, { useState, useEffect } from 'react';
import { Avatar, AvatarVideo, AvailableAvatarsResponse } from '@/types';

interface AvatarVideoGeneratorProps {
  shopId: number;
  onVideoGenerated?: (video: AvatarVideo) => void;
}

const AvatarVideoGenerator: React.FC<AvatarVideoGeneratorProps> = ({
  shopId,
  onVideoGenerated
}) => {
  const [availableAvatars, setAvailableAvatars] = useState<Avatar[]>([]);
  const [selectedAvatar, setSelectedAvatar] = useState<string>('marcus_primary');
  const [includeBusinessContext, setIncludeBusinessContext] = useState<boolean>(true);
  const [isGenerating, setIsGenerating] = useState<boolean>(false);
  const [generatedVideo, setGeneratedVideo] = useState<AvatarVideo | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [serviceStatus, setServiceStatus] = useState<string>('unknown');

  // Fetch available avatars on component mount
  useEffect(() => {
    fetchAvailableAvatars();
  }, []);

  const fetchAvailableAvatars = async () => {
    try {
      const response = await fetch('/api/v1/video/avatar/avatars');
      if (response.ok) {
        const data: { data: AvailableAvatarsResponse } = await response.json();
        setAvailableAvatars(data.data.avatars);
        setSelectedAvatar(data.data.default_avatar);
        setServiceStatus(data.data.service_status);
      } else {
        setError('Failed to fetch available avatars');
      }
    } catch (err) {
      setError('Error fetching avatars');
      console.error('Error fetching avatars:', err);
    }
  };

  const generateAvatarVideo = async () => {
    setIsGenerating(true);
    setError(null);
    setGeneratedVideo(null);

    try {
      const params = new URLSearchParams({
        shop_id: shopId.toString(),
        avatar_id: selectedAvatar,
        include_business_context: includeBusinessContext.toString()
      });

      const response = await fetch(`/api/v1/video/avatar/generate?${params}`, {
        method: 'POST',
      });

      if (response.ok) {
        const data: { data: AvatarVideo } = await response.json();
        setGeneratedVideo(data.data);
        onVideoGenerated?.(data.data);
      } else {
        const errorData = await response.json();
        setError(errorData.detail || 'Failed to generate avatar video');
      }
    } catch (err) {
      setError('Error generating avatar video');
      console.error('Error generating avatar video:', err);
    } finally {
      setIsGenerating(false);
    }
  };

  const getStatusBadge = (status: string) => {
    const statusColors = {
      available: 'bg-green-100 text-green-800',
      mock_mode: 'bg-yellow-100 text-yellow-800',
      error: 'bg-red-100 text-red-800'
    };

    return (
      <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${statusColors[status as keyof typeof statusColors] || 'bg-gray-100 text-gray-800'}`}>
        {status === 'available' ? 'Live' : status === 'mock_mode' ? 'Demo Mode' : 'Error'}
      </span>
    );
  };

  return (
    <div className="bg-white rounded-lg shadow-md p-6">
      <div className="flex items-center justify-between mb-6">
        <h3 className="text-lg font-semibold text-gray-900">
          AI Avatar Business Briefing
        </h3>
        {getStatusBadge(serviceStatus)}
      </div>

      {/* Avatar Selection */}
      <div className="mb-6">
        <label className="block text-sm font-medium text-gray-700 mb-3">
          Choose Your AI Analyst
        </label>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          {availableAvatars.map((avatar) => (
            <div
              key={avatar.id}
              className={`relative cursor-pointer rounded-lg border-2 p-4 transition-all ${
                selectedAvatar === avatar.id
                  ? 'border-blue-500 bg-blue-50'
                  : 'border-gray-200 hover:border-gray-300'
              }`}
              onClick={() => setSelectedAvatar(avatar.id)}
            >
              <div className="flex items-center space-x-3">
                <div className="flex-shrink-0">
                  <div className="w-12 h-12 bg-gradient-to-br from-blue-400 to-purple-500 rounded-full flex items-center justify-center text-white font-semibold">
                    {avatar.name.charAt(0)}
                  </div>
                </div>
                <div className="flex-1 min-w-0">
                  <p className="text-sm font-medium text-gray-900">
                    {avatar.name}
                  </p>
                  <p className="text-xs text-gray-500 truncate">
                    {avatar.description}
                  </p>
                </div>
              </div>
              {selectedAvatar === avatar.id && (
                <div className="absolute top-2 right-2">
                  <div className="w-4 h-4 bg-blue-500 rounded-full flex items-center justify-center">
                    <svg className="w-2 h-2 text-white" fill="currentColor" viewBox="0 0 8 8">
                      <path d="M6.564.75l-3.59 3.612-1.538-1.55L0 4.26l2.974 2.99L8 2.193z"/>
                    </svg>
                  </div>
                </div>
              )}
            </div>
          ))}
        </div>
      </div>

      {/* Options */}
      <div className="mb-6">
        <label className="flex items-center space-x-3">
          <input
            type="checkbox"
            checked={includeBusinessContext}
            onChange={(e) => setIncludeBusinessContext(e.target.checked)}
            className="h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded"
          />
          <span className="text-sm text-gray-700">
            Include detailed business analysis and insights
          </span>
        </label>
        <p className="text-xs text-gray-500 mt-1 ml-7">
          {includeBusinessContext 
            ? 'Generate a comprehensive business briefing with your latest data'
            : 'Generate a simple welcome message'
          }
        </p>
      </div>

      {/* Generate Button */}
      <button
        onClick={generateAvatarVideo}
        disabled={isGenerating || availableAvatars.length === 0}
        className={`w-full flex items-center justify-center px-4 py-3 border border-transparent text-sm font-medium rounded-md text-white transition-colors ${
          isGenerating || availableAvatars.length === 0
            ? 'bg-gray-400 cursor-not-allowed'
            : 'bg-blue-600 hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500'
        }`}
      >
        {isGenerating ? (
          <>
            <svg className="animate-spin -ml-1 mr-3 h-4 w-4 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
              <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
              <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
            </svg>
            Generating Your Briefing...
          </>
        ) : (
          <>
            <svg className="w-4 h-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 10l4.553-2.276A1 1 0 0121 8.618v6.764a1 1 0 01-1.447.894L15 14M5 18h8a2 2 0 002-2V8a2 2 0 00-2-2H5a2 2 0 00-2 2v8a2 2 0 002 2z" />
            </svg>
            Generate AI Briefing
          </>
        )}
      </button>

      {/* Error Display */}
      {error && (
        <div className="mt-4 p-4 bg-red-50 border border-red-200 rounded-md">
          <div className="flex">
            <svg className="w-5 h-5 text-red-400" fill="currentColor" viewBox="0 0 20 20">
              <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z" clipRule="evenodd" />
            </svg>
            <div className="ml-3">
              <p className="text-sm text-red-800">{error}</p>
            </div>
          </div>
        </div>
      )}

      {/* Generated Video Display */}
      {generatedVideo && (
        <div className="mt-6 p-4 bg-green-50 border border-green-200 rounded-md">
          <h4 className="text-sm font-medium text-green-800 mb-3">
            🎬 Your AI Briefing is Ready!
          </h4>
          
          <div className="space-y-3">
            {/* Video Player */}
            <div className="bg-black rounded-lg overflow-hidden">
              <video
                controls
                className="w-full h-64 object-cover"
                poster="/api/placeholder/640/360"
              >
                <source src={generatedVideo.video_url} type="video/mp4" />
                Your browser does not support the video tag.
              </video>
            </div>

            {/* Video Details */}
            <div className="grid grid-cols-2 gap-4 text-sm">
              <div>
                <span className="font-medium text-gray-700">Duration:</span>
                <span className="ml-2 text-gray-600">
                  {generatedVideo.duration_seconds}s
                </span>
              </div>
              <div>
                <span className="font-medium text-gray-700">Avatar:</span>
                <span className="ml-2 text-gray-600">
                  {availableAvatars.find(a => a.id === generatedVideo.avatar_id)?.name || generatedVideo.avatar_id}
                </span>
              </div>
              <div>
                <span className="font-medium text-gray-700">Resolution:</span>
                <span className="ml-2 text-gray-600">
                  {generatedVideo.resolution}
                </span>
              </div>
              <div>
                <span className="font-medium text-gray-700">Generated:</span>
                <span className="ml-2 text-gray-600">
                  {new Date(generatedVideo.generated_at).toLocaleTimeString()}
                </span>
              </div>
            </div>

            {/* Script Preview */}
            <div>
              <span className="font-medium text-gray-700">Script Preview:</span>
              <p className="mt-1 text-sm text-gray-600 bg-white p-3 rounded border">
                {generatedVideo.script_content.substring(0, 200)}
                {generatedVideo.script_content.length > 200 && '...'}
              </p>
            </div>

            {/* Mock Response Warning */}
            {generatedVideo.mock_response && (
              <div className="p-3 bg-yellow-50 border border-yellow-200 rounded">
                <p className="text-sm text-yellow-800">
                  ⚠️ {generatedVideo.message}
                </p>
              </div>
            )}

            {/* Action Buttons */}
            <div className="flex space-x-3">
              <a
                href={generatedVideo.video_url}
                download={`business-briefing-${generatedVideo.avatar_id}.mp4`}
                className="flex-1 bg-blue-600 text-white text-center py-2 px-4 rounded-md text-sm font-medium hover:bg-blue-700 transition-colors"
              >
                Download Video
              </a>
              <button
                onClick={() => navigator.clipboard.writeText(generatedVideo.video_url)}
                className="flex-1 bg-gray-600 text-white py-2 px-4 rounded-md text-sm font-medium hover:bg-gray-700 transition-colors"
              >
                Copy Link
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default AvatarVideoGenerator;