-- This script repairs the agent_jobs table by adding the missing application_id column.

ALTER TABLE agent_jobs
ADD COLUMN IF NOT EXISTS application_id UUID;

