-- Fix for test_cases status constraint
-- The current constraint only allows: pending, running, passed, failed, skipped, blocked
-- But the code is trying to use 'generated' status

-- Drop the existing constraint
ALTER TABLE test_cases DROP CONSTRAINT IF EXISTS valid_status;

-- Add the new constraint that includes 'generated'
ALTER TABLE test_cases ADD CONSTRAINT valid_status 
CHECK (status IN ('pending', 'running', 'passed', 'failed', 'skipped', 'blocked', 'generated'));

-- Verify the fix
DO $$
BEGIN
    IF EXISTS (
        SELECT 1 FROM pg_constraint 
        WHERE conname = 'valid_status' 
        AND conrelid = 'test_cases'::regclass
    ) THEN
        RAISE NOTICE '✅ Status constraint updated to include "generated" status';
    ELSE
        RAISE NOTICE '❌ Failed to update status constraint';
    END IF;
END $$;
