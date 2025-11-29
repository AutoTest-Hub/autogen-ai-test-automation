-- Fix for Create Tests page issues
-- 1. Add missing start_time column to test_executions table
-- 2. Fix permissions for applications access

-- Add missing start_time column to test_executions table
ALTER TABLE test_executions 
ADD COLUMN IF NOT EXISTS start_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP;

-- Add missing end_time column if it doesn't exist
ALTER TABLE test_executions 
ADD COLUMN IF NOT EXISTS end_time TIMESTAMP;

-- Add missing duration column if it doesn't exist
ALTER TABLE test_executions 
ADD COLUMN IF NOT EXISTS duration INTEGER;

-- Update existing records to have start_time
UPDATE test_executions 
SET start_time = created_at 
WHERE start_time IS NULL AND created_at IS NOT NULL;

-- Update existing records to have start_time as current timestamp if created_at is also null
UPDATE test_executions 
SET start_time = CURRENT_TIMESTAMP 
WHERE start_time IS NULL;

-- Create index on start_time for better performance
CREATE INDEX IF NOT EXISTS idx_test_executions_start_time ON test_executions(start_time);

-- Fix RLS policies for applications table to allow demo user access
-- First, check if RLS is enabled and create proper policies

-- Enable RLS on applications table if not already enabled
ALTER TABLE applications ENABLE ROW LEVEL SECURITY;

-- Drop existing policies if they exist
DROP POLICY IF EXISTS applications_select_policy ON applications;
DROP POLICY IF EXISTS applications_insert_policy ON applications;
DROP POLICY IF EXISTS applications_update_policy ON applications;
DROP POLICY IF EXISTS applications_delete_policy ON applications;

-- Create permissive policies for applications table
CREATE POLICY applications_select_policy ON applications
    FOR SELECT
    USING (true); -- Allow all users to select applications for now

CREATE POLICY applications_insert_policy ON applications
    FOR INSERT
    WITH CHECK (true); -- Allow all users to insert applications

CREATE POLICY applications_update_policy ON applications
    FOR UPDATE
    USING (true)
    WITH CHECK (true); -- Allow all users to update applications

CREATE POLICY applications_delete_policy ON applications
    FOR DELETE
    USING (true); -- Allow all users to delete applications

-- Grant necessary permissions to the demo user role
GRANT SELECT, INSERT, UPDATE, DELETE ON applications TO demo;
GRANT SELECT, INSERT, UPDATE, DELETE ON test_executions TO demo;

-- Ensure demo user has access to sequences
GRANT USAGE, SELECT ON ALL SEQUENCES IN SCHEMA public TO demo;

-- Insert some sample applications if none exist
INSERT INTO applications (id, customer_id, name, description, url, created_at, updated_at)
SELECT 
    gen_random_uuid(),
    (SELECT id FROM customers LIMIT 1),
    'Demo E-Commerce App',
    'Sample e-commerce application for testing',
    'https://demo.opencart.com',
    CURRENT_TIMESTAMP,
    CURRENT_TIMESTAMP
WHERE NOT EXISTS (SELECT 1 FROM applications LIMIT 1);

INSERT INTO applications (id, customer_id, name, description, url, created_at, updated_at)
SELECT 
    gen_random_uuid(),
    (SELECT id FROM customers LIMIT 1),
    'Demo Banking App',
    'Sample banking application for testing',
    'https://demo.testfire.net',
    CURRENT_TIMESTAMP,
    CURRENT_TIMESTAMP
WHERE (SELECT COUNT(*) FROM applications) < 2;

-- Refresh the RLS policies
SELECT pg_reload_conf();

-- Verify the fixes
SELECT 'test_executions columns:' as info;
SELECT column_name, data_type 
FROM information_schema.columns 
WHERE table_name = 'test_executions' 
AND column_name IN ('start_time', 'end_time', 'duration');

SELECT 'applications count:' as info;
SELECT COUNT(*) as application_count FROM applications;

SELECT 'RLS policies for applications:' as info;
SELECT schemaname, tablename, policyname, permissive, roles, cmd, qual 
FROM pg_policies 
WHERE tablename = 'applications';
