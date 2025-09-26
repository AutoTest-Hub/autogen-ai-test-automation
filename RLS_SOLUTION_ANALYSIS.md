# Row-Level Security (RLS) Issue Analysis & Solutions

## 🔍 **Current Problem**

The `test_cases` table has a Row-Level Security policy that blocks all INSERT operations:

```sql
Policy: customer_test_cases_isolation
Condition: customer_id = current_setting('app.current_customer_id')
Roles: app_read_only, app_read_write
```

**Issue**: The `app.current_customer_id` session variable is not being set, so the policy blocks all inserts.

## 🎯 **Solution Options (Ranked by Recommendation)**

### **Option 1: Fix Session Variable Setting (RECOMMENDED)**
**Approach**: Properly set the customer context in the database connection.

**Implementation**:
```python
# In database_postgres_full.py - modify connect() method
def connect(self):
    self.connection = psycopg2.connect(**self.db_config)
    self.connection.autocommit = True
    
    # Set customer context for RLS
    with self.connection.cursor() as cursor:
        cursor.execute("SELECT set_config('app.current_customer_id', %s, false)", 
                      (str(self.get_default_customer_id()),))
    
    logger.info("✅ Connected to PostgreSQL database")
    return True

def get_default_customer_id(self):
    # Get the demo customer ID from the database
    query = "SELECT id FROM customers WHERE email = 'demo@example.com' LIMIT 1"
    result = self.execute_query(query)
    return result[0]['id'] if result else None
```

**Pros**: 
- ✅ Maintains security compliance
- ✅ Proper enterprise solution
- ✅ No schema changes needed

**Cons**: 
- ⚠️ Requires code changes in database layer

---

### **Option 2: Modify RLS Policy (QUICK FIX)**
**Approach**: Update the RLS policy to be more permissive for the application user.

**Implementation**:
```sql
-- Drop existing policy
DROP POLICY customer_test_cases_isolation ON test_cases;

-- Create new policy that allows app_user full access
CREATE POLICY customer_test_cases_isolation ON test_cases
    FOR ALL TO app_read_write, app_read_only
    USING (
        customer_id = COALESCE(
            current_setting('app.current_customer_id', true)::uuid,
            (SELECT id FROM customers LIMIT 1)  -- Fallback to first customer
        )
    );
```

**Pros**: 
- ✅ Quick fix - no code changes
- ✅ Maintains some security
- ✅ Works immediately

**Cons**: 
- ⚠️ Less secure (fallback mechanism)
- ⚠️ May not meet strict compliance requirements

---

### **Option 3: Bypass RLS for Application User (FASTEST)**
**Approach**: Grant BYPASSRLS privilege to the application user.

**Implementation**:
```sql
ALTER USER app_user BYPASSRLS;
```

**Pros**: 
- ✅ Immediate fix
- ✅ No code or policy changes needed
- ✅ Simple one-line solution

**Cons**: 
- ❌ Completely bypasses security
- ❌ Not suitable for production
- ❌ Violates SOC 2 compliance principles

---

### **Option 4: Disable RLS Temporarily (DEVELOPMENT ONLY)**
**Approach**: Disable RLS on the test_cases table.

**Implementation**:
```sql
ALTER TABLE test_cases DISABLE ROW LEVEL SECURITY;
```

**Pros**: 
- ✅ Immediate fix
- ✅ Simple solution

**Cons**: 
- ❌ Removes all security
- ❌ Only suitable for development
- ❌ Must be re-enabled for production

---

## 🏆 **Recommended Solution: Option 1**

**Why Option 1 is best**:
1. **Enterprise-Ready**: Maintains proper security architecture
2. **SOC 2 Compliant**: Preserves audit trail and data isolation
3. **Scalable**: Works with multi-tenant scenarios
4. **Future-Proof**: Supports proper customer context switching

**Implementation Steps**:
1. Modify `DatabaseManager.connect()` to set customer context
2. Add helper method to get default customer ID
3. Update agent processor to ensure customer context is maintained
4. Test with multiple customers to verify isolation

## 🔧 **Quick Test Fix (Option 2)**

If you want to test immediately while we implement Option 1:

```sql
-- Run this to make the policy more permissive
DROP POLICY customer_test_cases_isolation ON test_cases;
CREATE POLICY customer_test_cases_isolation ON test_cases
    FOR ALL TO app_read_write, app_read_only
    USING (true);  -- Allow all for now
```

This will let you see the full workflow working while we implement the proper solution.

## 📋 **Next Steps**

1. **Immediate**: Apply quick fix (Option 2) to test full workflow
2. **Short-term**: Implement proper session variable setting (Option 1)
3. **Long-term**: Add customer context switching for multi-tenant support
