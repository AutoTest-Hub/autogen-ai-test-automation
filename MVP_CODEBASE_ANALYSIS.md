# MVP Codebase Analysis & Modification Plan

## 🔍 **Current Architecture Analysis**

### **Database Schema (Current State)**
```sql
-- test_cases table (CURRENT - needs modification)
test_cases:
├── id (UUID)
├── test_suite_id (UUID) ✅ Good - maintains suite association
├── customer_id (UUID) ✅ Good - customer isolation
├── name (VARCHAR) ✅ Good
├── description (TEXT) ✅ Good
├── test_type (VARCHAR) ✅ Good
├── priority (VARCHAR) ✅ Good
├── test_steps (JSONB) ❌ REMOVE - replace with file path
├── test_data (JSONB) ❌ REMOVE - replace with file path
├── expected_result (TEXT) ❌ REMOVE - replace with file path
├── status (VARCHAR) ✅ Good
├── actual_result (TEXT) ✅ Good - for execution results
├── error_message (TEXT) ✅ Good - for execution results
└── execution_time_ms (INTEGER) ✅ Good - for execution results

-- test_suites table (CURRENT - good structure)
test_suites:
├── id (UUID) ✅ Good
├── customer_id (UUID) ✅ Good
├── application_id (UUID) ✅ Good
├── name (VARCHAR) ✅ Good
├── description (TEXT) ✅ Good
├── test_type (VARCHAR) ✅ Good
├── status (VARCHAR) ✅ Good
├── configuration (JSONB) ✅ Good
├── total_test_cases (INTEGER) ✅ Good - for suite management
├── passed_test_cases (INTEGER) ✅ Good
├── failed_test_cases (INTEGER) ✅ Good
└── success_rate (NUMERIC) ✅ Good
```

### **Current Agent Processor Flow**
```python
# real_agent_processor.py (CURRENT - needs modification)
1. _discovery_phase() ✅ Good - generates test scenarios
2. _generation_phase() ✅ Good - creates test case metadata
3. _code_generation_phase() ❌ MODIFY - currently saves to DB, need file storage
4. _validation_phase() ✅ Good - validates test suite
5. _save_test_case_to_db() ❌ MODIFY - need to add file storage logic
```

### **Current Database Manager**
```python
# database_postgres_full.py (CURRENT - needs extension)
- Has good customer isolation with RLS ✅
- Has test case CRUD operations ❌ Need to modify for file paths
- Has proper audit logging ✅
- Missing file storage integration ❌ Need to add
```

## 🎯 **MVP Modification Plan**

### **Phase 1: Database Schema Enhancement**

#### **Modify test_cases table (ADD columns, don't remove existing)**
```sql
-- Add file storage columns to existing test_cases table
ALTER TABLE test_cases ADD COLUMN test_file_path VARCHAR(1000);
ALTER TABLE test_cases ADD COLUMN config_file_path VARCHAR(1000);
ALTER TABLE test_cases ADD COLUMN generated_from_intent TEXT;
ALTER TABLE test_cases ADD COLUMN generation_model VARCHAR(50) DEFAULT 'gpt-4';
ALTER TABLE test_cases ADD COLUMN generation_timestamp TIMESTAMP WITH TIME ZONE;
ALTER TABLE test_cases ADD COLUMN code_confidence_score DECIMAL(3,2);
ALTER TABLE test_cases ADD COLUMN file_size_bytes BIGINT;
ALTER TABLE test_cases ADD COLUMN file_checksum VARCHAR(64);
ALTER TABLE test_cases ADD COLUMN last_modified TIMESTAMP WITH TIME ZONE;
ALTER TABLE test_cases ADD COLUMN success_rate DECIMAL(5,2);
ALTER TABLE test_cases ADD COLUMN avg_execution_time_ms INTEGER;

-- Keep existing columns for backward compatibility during transition
-- test_steps, test_data, expected_result can be deprecated later
```

### **Phase 2: File Storage Manager (NEW component)**

#### **Create universal file storage interface**
```python
# NEW FILE: api/file_storage_manager.py
class FileStorageManager(ABC):
    @abstractmethod
    def save_test_file(self, customer_id: str, suite_id: str, test_case: Dict) -> str
    @abstractmethod
    def load_test_file(self, file_path: str) -> str
    @abstractmethod
    def delete_test_file(self, file_path: str) -> bool
    @abstractmethod
    def file_exists(self, file_path: str) -> bool

class LocalFileManager(FileStorageManager):
    # For on-premise deployments
    
class S3FileManager(FileStorageManager):
    # For SaaS deployments
    
class AzureBlobManager(FileStorageManager):
    # For Azure deployments
    
class GCSFileManager(FileStorageManager):
    # For Google Cloud deployments
```

### **Phase 3: Agent Processor Modifications**

#### **Modify real_agent_processor.py**
```python
# MODIFY EXISTING: api/real_agent_processor.py

class RealAgentProcessor:
    def __init__(self):
        # ADD: File storage manager
        self.file_manager = self._get_file_manager()
    
    def _get_file_manager(self):
        # Factory pattern for different storage backends
        storage_type = os.getenv('STORAGE_TYPE', 'local')
        if storage_type == 's3':
            return S3FileManager()
        elif storage_type == 'azure':
            return AzureBlobManager()
        elif storage_type == 'gcs':
            return GCSFileManager()
        else:
            return LocalFileManager()
    
    # MODIFY EXISTING METHOD
    async def _code_generation_phase(self, job_id: UUID, test_cases: List[Dict], test_suite_id: UUID):
        """MODIFIED: Generate and save test files instead of DB storage"""
        
        for test_case in test_cases:
            # 1. Generate Playwright code
            playwright_code = self._generate_playwright_code(test_case)
            
            # 2. Save to file storage
            file_path = self.file_manager.save_test_file(
                customer_id=customer_id,
                suite_id=test_suite_id,
                test_case={**test_case, 'code': playwright_code}
            )
            
            # 3. Save metadata to database (with file path)
            test_case_id = self._save_test_case_metadata(test_case, test_suite_id, file_path, job_id)
    
    # NEW METHOD
    def _generate_playwright_code(self, test_case: Dict) -> str:
        """Generate actual Playwright test code"""
        return f'''
import pytest
from playwright.sync_api import Page, expect

def test_{test_case['name'].lower().replace(' ', '_')}(page: Page):
    """
    {test_case['description']}
    Generated from: {test_case.get('intent', 'AI Agent')}
    """
    # Navigate to application
    page.goto("{test_case.get('base_url', 'https://example.com')}")
    
    # Test steps
    {self._generate_step_code(test_case.get('steps', []))}
    
    # Assertions
    {self._generate_assertions(test_case.get('expected_result', 'Test should pass'))}
'''
    
    # MODIFY EXISTING METHOD
    def _save_test_case_to_db(self, test_case: Dict, test_suite_id: UUID, file_path: str, job_id: UUID) -> UUID:
        """MODIFIED: Save test case metadata with file path"""
        query = """
        INSERT INTO test_cases (
            id, test_suite_id, customer_id, name, description, test_type, priority,
            test_file_path, generated_from_intent, generation_model, generation_timestamp,
            code_confidence_score, file_checksum, status
        ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """
        # Implementation with file metadata
```

### **Phase 4: Database Manager Extensions**

#### **Extend database_postgres_full.py**
```python
# MODIFY EXISTING: api/database_postgres_full.py

class TestCase:
    # ADD NEW METHODS
    @staticmethod
    def get_test_code(test_case_id: UUID) -> str:
        """Load test code from file storage"""
        test_case = TestCase.get_by_id(test_case_id)
        if test_case and test_case['test_file_path']:
            file_manager = get_file_manager()
            return file_manager.load_test_file(test_case['test_file_path'])
        return None
    
    @staticmethod
    def update_file_metadata(test_case_id: UUID, file_path: str, checksum: str, size: int):
        """Update file metadata after saving"""
        query = """
        UPDATE test_cases 
        SET test_file_path = %s, file_checksum = %s, file_size_bytes = %s, 
            last_modified = NOW()
        WHERE id = %s
        """
        db.execute_command(query, (file_path, checksum, size, test_case_id))
    
    # MODIFY EXISTING METHODS to handle file paths
    @staticmethod
    def create_with_file(test_case_data: Dict, file_path: str) -> UUID:
        """Create test case with file path"""
        # Enhanced creation logic
```

### **Phase 5: Test Suite Management**

#### **Enhance test suite associations**
```python
# MODIFY EXISTING: Ensure test suite properly tracks test cases

class TestSuite:
    @staticmethod
    def get_test_cases_with_files(suite_id: UUID) -> List[Dict]:
        """Get all test cases in suite with file information"""
        query = """
        SELECT tc.*, 
               CASE WHEN tc.test_file_path IS NOT NULL THEN true ELSE false END as has_file
        FROM test_cases tc 
        WHERE tc.test_suite_id = %s 
        ORDER BY tc.created_at
        """
        return db.execute_query(query, (suite_id,))
    
    @staticmethod
    def update_test_case_association(suite_id: UUID, test_case_ids: List[UUID]):
        """Allow users to modify test case associations"""
        # Remove existing associations
        db.execute_command("DELETE FROM test_cases WHERE test_suite_id = %s", (suite_id,))
        
        # Add new associations
        for test_case_id in test_case_ids:
            db.execute_command(
                "UPDATE test_cases SET test_suite_id = %s WHERE id = %s",
                (suite_id, test_case_id)
            )
```

## 🚀 **Implementation Strategy**

### **Files to Modify (NOT create new)**
1. ✅ `database/schema.sql` - Add new columns to test_cases
2. ✅ `api/real_agent_processor.py` - Modify to use file storage
3. ✅ `api/database_postgres_full.py` - Extend with file operations
4. ✅ `api/main_postgres_full.py` - Add file storage configuration

### **Files to Create (NEW components)**
1. 🆕 `api/file_storage_manager.py` - Universal file storage interface
2. 🆕 `api/test_execution_manager.py` - Execute tests from files
3. 🆕 `api/config_manager.py` - Storage configuration management

### **Configuration Changes**
```python
# Environment variables for storage backend
STORAGE_TYPE=local|s3|azure|gcs
STORAGE_BASE_PATH=/opt/test-platform/data  # for local
S3_BUCKET=test-automation-platform         # for S3
AZURE_CONTAINER=test-files                 # for Azure
GCS_BUCKET=test-automation-files           # for GCS
```

## 🎯 **MVP Success Criteria**

1. ✅ **Backward Compatibility**: Existing test cases continue to work
2. ✅ **File Storage**: New test cases saved as actual Playwright files
3. ✅ **Suite Management**: Users can modify test case associations
4. ✅ **Multi-Backend**: Support local, S3, Azure, GCS storage
5. ✅ **E2E Testing**: All 4 agents work with file-based storage
6. ✅ **No Regressions**: Existing functionality preserved

This approach modifies the existing codebase incrementally while maintaining all current functionality!
