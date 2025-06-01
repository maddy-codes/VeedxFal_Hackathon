-- SQL script to create async video generation tables in Supabase (PostgreSQL)

-- Create video_jobs table for tracking video generation jobs
CREATE TABLE IF NOT EXISTS video_jobs (
    job_id TEXT PRIMARY KEY,
    shop_id INTEGER NOT NULL,
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
    job_id TEXT NOT NULL,
    shop_id INTEGER NOT NULL,
    script_content TEXT NOT NULL,
    word_count INTEGER DEFAULT 0,
    estimated_duration FLOAT DEFAULT 0,
    generated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    FOREIGN KEY (job_id) REFERENCES video_jobs(job_id)
);

-- Create generated_videos table for storing video metadata
CREATE TABLE IF NOT EXISTS generated_videos (
    video_id TEXT PRIMARY KEY,
    shop_id INTEGER NOT NULL,
    job_id TEXT,
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
    metadata JSONB,
    FOREIGN KEY (job_id) REFERENCES video_jobs(job_id)
);

-- Create indexes for better performance
CREATE INDEX IF NOT EXISTS idx_video_jobs_status ON video_jobs(status);
CREATE INDEX IF NOT EXISTS idx_video_jobs_shop_id ON video_jobs(shop_id);
CREATE INDEX IF NOT EXISTS idx_video_jobs_user_id ON video_jobs(user_id);
CREATE INDEX IF NOT EXISTS idx_video_jobs_created_at ON video_jobs(created_at);
CREATE INDEX IF NOT EXISTS idx_video_scripts_job_id ON video_scripts(job_id);
CREATE INDEX IF NOT EXISTS idx_video_scripts_shop_id ON video_scripts(shop_id);
CREATE INDEX IF NOT EXISTS idx_generated_videos_job_id ON generated_videos(job_id);
CREATE INDEX IF NOT EXISTS idx_generated_videos_shop_id ON generated_videos(shop_id);
CREATE INDEX IF NOT EXISTS idx_generated_videos_generated_at ON generated_videos(generated_at);

-- Add RLS (Row Level Security) policies if needed
-- ALTER TABLE video_jobs ENABLE ROW LEVEL SECURITY;
-- ALTER TABLE video_scripts ENABLE ROW LEVEL SECURITY;
-- ALTER TABLE generated_videos ENABLE ROW LEVEL SECURITY;

-- Example RLS policies (uncomment and modify as needed):
-- CREATE POLICY "Users can view their own video jobs" ON video_jobs
--     FOR SELECT USING (auth.uid()::text = user_id);

-- CREATE POLICY "Users can insert their own video jobs" ON video_jobs
--     FOR INSERT WITH CHECK (auth.uid()::text = user_id);

-- CREATE POLICY "Users can update their own video jobs" ON video_jobs
--     FOR UPDATE USING (auth.uid()::text = user_id);