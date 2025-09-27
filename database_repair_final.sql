-- Final Database Repair Script for Remaining Issues
-- This script addresses the specific issues found in the latest console logs

-- 1. Add missing subscription_plans table
CREATE TABLE IF NOT EXISTS subscription_plans (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(100) NOT NULL UNIQUE,
    description TEXT,
    price_monthly DECIMAL(10,2),
    price_yearly DECIMAL(10,2),
    features JSONB DEFAULT '{}',
    max_users INTEGER,
    max_applications INTEGER,
    max_test_executions_per_month INTEGER,
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- 2. Add missing subscription_plan_id column to customers table
ALTER TABLE customers
ADD COLUMN IF NOT EXISTS subscription_plan_id UUID REFERENCES subscription_plans(id);

-- 3. Add missing message column to agent_job_activities table
ALTER TABLE agent_job_activities
ADD COLUMN IF NOT EXISTS message TEXT;

-- 4. Add unique constraint to customer_users table for ON CONFLICT to work
ALTER TABLE customer_users
ADD CONSTRAINT IF NOT EXISTS customer_users_email_unique UNIQUE (email);

-- 5. Insert default subscription plans
INSERT INTO subscription_plans (id, name, description, price_monthly, price_yearly, max_users, max_applications, max_test_executions_per_month) VALUES 
    ('11111111-1111-1111-1111-111111111111', 'Starter', 'Basic plan for small teams', 29.99, 299.99, 5, 3, 1000),
    ('22222222-2222-2222-2222-222222222222', 'Professional', 'Advanced plan for growing teams', 99.99, 999.99, 25, 10, 5000),
    ('33333333-3333-3333-3333-333333333333', 'Enterprise', 'Full-featured plan for large organizations', 299.99, 2999.99, 100, 50, 25000)
ON CONFLICT (name) DO NOTHING;

-- 6. Update existing customers to have a subscription plan
UPDATE customers 
SET subscription_plan_id = '22222222-2222-2222-2222-222222222222' 
WHERE subscription_plan_id IS NULL;

-- 7. Create indexes for the new columns
CREATE INDEX IF NOT EXISTS idx_customers_subscription_plan_id ON customers(subscription_plan_id);
CREATE INDEX IF NOT EXISTS idx_subscription_plans_name ON subscription_plans(name);
CREATE INDEX IF NOT EXISTS idx_customer_users_email ON customer_users(email);

-- 8. Update trigger for subscription_plans
DROP TRIGGER IF EXISTS update_subscription_plans_updated_at ON subscription_plans;
CREATE TRIGGER update_subscription_plans_updated_at
    BEFORE UPDATE ON subscription_plans
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- 9. Verify the final repair
DO $$
DECLARE
    table_count INTEGER;
    subscription_plans_count INTEGER;
    customers_with_plans INTEGER;
BEGIN
    -- Count total tables
    SELECT COUNT(*) INTO table_count
    FROM information_schema.tables 
    WHERE table_schema = 'public' 
    AND table_type = 'BASE TABLE';
    
    -- Count subscription plans
    SELECT COUNT(*) INTO subscription_plans_count FROM subscription_plans;
    
    -- Count customers with subscription plans
    SELECT COUNT(*) INTO customers_with_plans FROM customers WHERE subscription_plan_id IS NOT NULL;
    
    RAISE NOTICE 'Final database repair completed:';
    RAISE NOTICE '  - Total tables: %', table_count;
    RAISE NOTICE '  - Subscription plans: %', subscription_plans_count;
    RAISE NOTICE '  - Customers with plans: %', customers_with_plans;
    
    -- Check for specific fixes
    IF EXISTS (SELECT 1 FROM information_schema.tables WHERE table_name = 'subscription_plans') THEN
        RAISE NOTICE '✅ subscription_plans table created';
    END IF;
    
    IF EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name = 'customers' AND column_name = 'subscription_plan_id') THEN
        RAISE NOTICE '✅ subscription_plan_id column added to customers';
    END IF;
    
    IF EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name = 'agent_job_activities' AND column_name = 'message') THEN
        RAISE NOTICE '✅ message column added to agent_job_activities';
    END IF;
    
    IF EXISTS (SELECT 1 FROM information_schema.table_constraints WHERE table_name = 'customer_users' AND constraint_name = 'customer_users_email_unique') THEN
        RAISE NOTICE '✅ unique constraint added to customer_users.email';
    END IF;
END $$;
