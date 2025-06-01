-- Simple generated_videos table for storing video links
-- Run this in your Supabase SQL Editor

CREATE TABLE IF NOT EXISTS generated_videos (
    video_id TEXT PRIMARY KEY DEFAULT gen_random_uuid()::text,
    shop_id BIGINT NOT NULL REFERENCES stores(id) ON DELETE CASCADE,
    video_url TEXT,
    script_content TEXT,
    duration_seconds FLOAT,
    format TEXT DEFAULT 'mp4',
    resolution TEXT DEFAULT '1080p',
    avatar_id TEXT DEFAULT 'marcus_primary',
    ai_provider TEXT DEFAULT 'fal_ai',
    generated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    view_count INTEGER DEFAULT 0,
    metadata JSONB DEFAULT '{}'::jsonb
);

-- Create indexes for performance
CREATE INDEX IF NOT EXISTS idx_generated_videos_shop_id ON generated_videos(shop_id);
CREATE INDEX IF NOT EXISTS idx_generated_videos_generated_at ON generated_videos(generated_at);

-- Enable RLS for security
ALTER TABLE generated_videos ENABLE ROW LEVEL SECURITY;

-- RLS Policy: Users can only access videos from their stores
CREATE POLICY generated_videos_isolation_policy ON generated_videos
    FOR ALL
    USING (
        shop_id IN (
            SELECT id FROM stores 
            WHERE auth.uid()::text = (shop_config->>'user_id')::text
        )
    );