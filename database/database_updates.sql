-- Database Updates for Agent Processing Fixes
-- Run this script to update your existing database schema

-- 1. Add missing columns to test_cases table if they don't exist
DO $$ 
BEGIN
    -- Add customer_id column if it doesn't exist
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns 
                   WHERE table_name = 'test_cases' AND column_name = 'customer_id') THEN
        ALTER TABLE test_cases ADD COLUMN customer_id UUID REFERENCES customers(id);
    END IF;
    
    -- Add test_steps JSONB column if it doesn't exist
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns 
                   WHERE table_name = 'test_cases' AND column_name = 'test_steps') THEN
        ALTER TABLE test_cases ADD COLUMN test_steps JSONB;
    END IF;
    
    -- Ensure test_type column exists (should already exist)
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns 
                   WHERE table_name = 'test_cases' AND column_name = 'test_type') THEN
        ALTER TABLE test_cases ADD COLUMN test_type VARCHAR(50);
    END IF;
END $$;

-- 2. Update existing test_cases to have customer_id if they don't
UPDATE test_cases 
SET customer_id = (SELECT id FROM customers LIMIT 1)
WHERE customer_id IS NULL;

-- 3. Verify the agent_jobs table has all required columns
DO $$ 
BEGIN
    -- Add progress_percentage if missing
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns 
                   WHERE table_name = 'agent_jobs' AND column_name = 'progress_percentage') THEN
        ALTER TABLE agent_jobs ADD COLUMN progress_percentage INTEGER DEFAULT 0;
    END IF;
    
    -- Add current_agent if missing
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns 
                   WHERE table_name = 'agent_jobs' AND column_name = 'current_agent') THEN
        ALTER TABLE agent_jobs ADD COLUMN current_agent VARCHAR(100);
    END IF;
    
    -- Add current_step if missing
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns 
                   WHERE table_name = 'agent_jobs' AND column_name = 'current_step') THEN
        ALTER TABLE agent_jobs ADD COLUMN current_step VARCHAR(200);
    END IF;
END $$;

-- 4. Verify agent_job_activities table structure
DO $$ 
BEGIN
    -- Add progress_percentage if missing
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns 
                   WHERE table_name = 'agent_job_activities' AND column_name = 'progress_percentage') THEN
        ALTER TABLE agent_job_activities ADD COLUMN progress_percentage INTEGER DEFAULT 0;
    END IF;
    
    -- Add message if missing
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns 
                   WHERE table_name = 'agent_job_activities' AND column_name = 'message') THEN
        ALTER TABLE agent_job_activities ADD COLUMN message TEXT;
    END IF;
END $$;

-- 5. Clean up any old test data that might cause conflicts
DELETE FROM agent_job_activities WHERE agent_job_id NOT IN (SELECT id FROM agent_jobs);
DELETE FROM agent_jobs WHERE status = 'pending' AND created_at < NOW() - INTERVAL '1 hour';

-- 6. Grant permissions to app_user for any new columns
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO app_user;
GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO app_user;

-- 7. Refresh materialized views if any exist
-- (Add any materialized view refreshes here if needed)

SELECT 'Database updates completed successfully!' as result;
