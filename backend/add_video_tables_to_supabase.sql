-- Add video generation tables to existing Supabase database
-- Run this in your Supabase SQL Editor

-- Create video_jobs table for tracking video generation jobs
CREATE TABLE IF NOT EXISTS video_jobs (
    job_id TEXT PRIMARY KEY,
    shop_id BIGINT NOT NULL REFERENCES stores(id) ON DELETE CASCADE,
    user_id TEXT NOT NULL,
    status TEXT DEFAULT 'pending',
    request_data JSONB,
    progress INTEGER DEFAULT 0,
    current_step TEXT DEFAULT 'pending',
    error_message TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    started_at TIMESTAMP WITH TIME ZONE,
    completed_at TIMESTAMP WITH TIME ZONE,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    video_id TEXT
);

-- Create video_scripts table for storing generated scripts
CREATE TABLE IF NOT EXISTS video_scripts (
    script_id TEXT PRIMARY KEY,
    job_id TEXT NOT NULL REFERENCES video_jobs(job_id) ON DELETE CASCADE,
    shop_id BIGINT NOT NULL REFERENCES stores(id) ON DELETE CASCADE,
    script_content TEXT NOT NULL,
    word_count INTEGER DEFAULT 0,
    estimated_duration FLOAT DEFAULT 0,
    generated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create generated_videos table for storing video metadata
CREATE TABLE IF NOT EXISTS generated_videos (
    video_id TEXT PRIMARY KEY,
    shop_id BIGINT NOT NULL REFERENCES stores(id) ON DELETE CASCADE,
    job_id TEXT REFERENCES video_jobs(job_id) ON DELETE CASCADE,
    video_url TEXT,
    script_content TEXT,
    audio_url TEXT,
    duration_seconds FLOAT,
    file_size_bytes BIGINT,
    resolution TEXT,
    format TEXT DEFAULT 'mp4',
    generated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    expires_at TIMESTAMP WITH TIME ZONE,
    view_count INTEGER DEFAULT 0,
    metadata JSONB
);

-- Create performance indexes
CREATE INDEX IF NOT EXISTS idx_video_jobs_status ON video_jobs(status);
CREATE INDEX IF NOT EXISTS idx_video_jobs_shop_id ON video_jobs(shop_id);
CREATE INDEX IF NOT EXISTS idx_video_jobs_user_id ON video_jobs(user_id);
CREATE INDEX IF NOT EXISTS idx_video_jobs_created_at ON video_jobs(created_at);
CREATE INDEX IF NOT EXISTS idx_video_scripts_job_id ON video_scripts(job_id);
CREATE INDEX IF NOT EXISTS idx_video_scripts_shop_id ON video_scripts(shop_id);
CREATE INDEX IF NOT EXISTS idx_generated_videos_job_id ON generated_videos(job_id);
CREATE INDEX IF NOT EXISTS idx_generated_videos_shop_id ON generated_videos(shop_id);
CREATE INDEX IF NOT EXISTS idx_generated_videos_generated_at ON generated_videos(generated_at);

-- Enable RLS for security
ALTER TABLE video_jobs ENABLE ROW LEVEL SECURITY;
ALTER TABLE video_scripts ENABLE ROW LEVEL SECURITY;
ALTER TABLE generated_videos ENABLE ROW LEVEL SECURITY;

-- RLS Policies: Users can only access their own video data
CREATE POLICY video_jobs_isolation_policy ON video_jobs
    FOR ALL
    USING (
        shop_id IN (
            SELECT id FROM stores 
            WHERE auth.uid()::text = (shop_config->>'user_id')::text
        )
    );

CREATE POLICY video_scripts_isolation_policy ON video_scripts
    FOR ALL
    USING (
        shop_id IN (
            SELECT id FROM stores 
            WHERE auth.uid()::text = (shop_config->>'user_id')::text
        )
    );

CREATE POLICY generated_videos_isolation_policy ON generated_videos
    FOR ALL
    USING (
        shop_id IN (
            SELECT id FROM stores 
            WHERE auth.uid()::text = (shop_config->>'user_id')::text
        )
    );

-- Add updated_at trigger for video_jobs
CREATE TRIGGER update_video_jobs_updated_at 
    BEFORE UPDATE ON video_jobs 
    FOR EACH ROW 
    EXECUTE FUNCTION update_updated_at_column();