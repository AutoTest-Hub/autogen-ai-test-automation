"""
Duplicate Detection and Hybrid Update Service
Handles intelligent test case management with duplicate prevention and update logic
"""

import logging
from typing import List, Dict, Optional, Tuple
from uuid import UUID
from datetime import datetime, timezone
import difflib
import hashlib
import json
from database_postgres_full import TestCase, TestSuite, Application

logger = logging.getLogger(__name__)

class DuplicateDetectionService:
    """Service for detecting duplicate tests and managing hybrid updates"""
    
    def __init__(self):
        self.similarity_threshold = 0.8  # 80% similarity threshold
        self.keyword_weight = 0.4
        self.description_weight = 0.6
    
    def calculate_text_similarity(self, text1: str, text2: str) -> float:
        """Calculate similarity between two text strings using difflib"""
        if not text1 or not text2:
            return 0.0
        
        text1_clean = text1.lower().strip()
        text2_clean = text2.lower().strip()
        
        if text1_clean == text2_clean:
            return 1.0
        
        # Use sequence matcher for similarity
        matcher = difflib.SequenceMatcher(None, text1_clean, text2_clean)
        return matcher.ratio()
    
    def extract_keywords(self, text: str) -> List[str]:
        """Extract key testing keywords from text"""
        testing_keywords = [
            'login', 'register', 'signup', 'checkout', 'payment', 'cart', 'search',
            'filter', 'form', 'validation', 'submit', 'upload', 'download', 'profile',
            'dashboard', 'settings', 'navigation', 'menu', 'button', 'click', 'verify',
            'test', 'check', 'validate', 'confirm', 'error', 'success', 'fail'
        ]
        
        text_lower = text.lower()
        found_keywords = []
        
        for keyword in testing_keywords:
            if keyword in text_lower:
                found_keywords.append(keyword)
        
        return found_keywords
    
    def calculate_keyword_similarity(self, keywords1: List[str], keywords2: List[str]) -> float:
        """Calculate similarity based on common keywords"""
        if not keywords1 or not keywords2:
            return 0.0
        
        set1 = set(keywords1)
        set2 = set(keywords2)
        
        intersection = len(set1.intersection(set2))
        union = len(set1.union(set2))
        
        return intersection / union if union > 0 else 0.0
    
    def calculate_overall_similarity(self, test1: Dict, test2: Dict) -> float:
        """Calculate overall similarity between two tests"""
        # Text similarity (name + description)
        name_sim = self.calculate_text_similarity(
            test1.get('name', ''), test2.get('name', '')
        )
        desc_sim = self.calculate_text_similarity(
            test1.get('description', ''), test2.get('description', '')
        )
        text_similarity = (name_sim + desc_sim) / 2
        
        # Keyword similarity
        keywords1 = self.extract_keywords(f"{test1.get('name', '')} {test1.get('description', '')}")
        keywords2 = self.extract_keywords(f"{test2.get('name', '')} {test2.get('description', '')}")
        keyword_similarity = self.calculate_keyword_similarity(keywords1, keywords2)
        
        # Weighted overall similarity
        overall_similarity = (
            text_similarity * self.description_weight +
            keyword_similarity * self.keyword_weight
        )
        
        return overall_similarity
    
    def find_duplicate_tests(self, customer_id: UUID, application_id: UUID, 
                           new_test_description: str, new_test_name: str = None) -> List[Dict]:
        """Find potential duplicate tests for a given test description"""
        try:
            # Get existing tests for the application
            existing_tests = TestCase.get_by_application(application_id)
            
            duplicates = []
            new_test = {
                'name': new_test_name or 'New Test',
                'description': new_test_description
            }
            
            for test in existing_tests:
                similarity = self.calculate_overall_similarity(new_test, test)
                
                if similarity >= self.similarity_threshold:
                    duplicates.append({
                        'test_id': str(test['id']),
                        'name': test['name'],
                        'description': test['description'],
                        'similarity_score': similarity,
                        'created_at': test['created_at'].isoformat() if test['created_at'] else None,
                        'last_updated': test['updated_at'].isoformat() if test['updated_at'] else None,
                        'status': test['status']
                    })
            
            # Sort by similarity score (highest first)
            duplicates.sort(key=lambda x: x['similarity_score'], reverse=True)
            
            return duplicates
            
        except Exception as e:
            logger.error(f"Error finding duplicate tests: {e}")
            return []
    
    def should_update_existing_test(self, existing_test: Dict, new_test_data: Dict) -> Tuple[bool, str]:
        """Determine if an existing test should be updated with new data"""
        reasons = []
        
        # Check if new test has more detailed description
        if len(new_test_data.get('description', '')) > len(existing_test.get('description', '')):
            reasons.append("New test has more detailed description")
        
        # Check if existing test is outdated (older than 30 days without updates)
        if existing_test.get('updated_at'):
            try:
                last_update = datetime.fromisoformat(existing_test['updated_at'].replace('Z', '+00:00'))
                days_since_update = (datetime.now(timezone.utc) - last_update).days
                if days_since_update > 30:
                    reasons.append(f"Existing test hasn't been updated in {days_since_update} days")
            except:
                pass
        
        # Check if existing test has failed status
        if existing_test.get('status') in ['failed', 'deprecated']:
            reasons.append(f"Existing test has {existing_test.get('status')} status")
        
        # Check if new test has additional test steps or scenarios
        new_keywords = self.extract_keywords(new_test_data.get('description', ''))
        existing_keywords = self.extract_keywords(existing_test.get('description', ''))
        
        if len(new_keywords) > len(existing_keywords):
            reasons.append("New test covers additional scenarios")
        
        should_update = len(reasons) > 0
        reason_text = "; ".join(reasons) if reasons else "No significant improvements found"
        
        return should_update, reason_text
    
    def generate_test_hash(self, test_data: Dict) -> str:
        """Generate a hash for test data to detect exact duplicates"""
        # Create a normalized representation of the test
        normalized_data = {
            'name': test_data.get('name', '').lower().strip(),
            'description': test_data.get('description', '').lower().strip(),
            'application_url': test_data.get('application_url', '').lower().strip()
        }
        
        # Create hash from normalized data
        data_string = json.dumps(normalized_data, sort_keys=True)
        return hashlib.md5(data_string.encode()).hexdigest()
    
    def analyze_test_coverage_gaps(self, customer_id: UUID, application_id: UUID, 
                                 new_test_description: str) -> Dict:
        """Analyze what new coverage the test would add"""
        try:
            existing_tests = TestCase.get_by_application(application_id)
            
            # Extract keywords from new test
            new_keywords = set(self.extract_keywords(new_test_description))
            
            # Extract keywords from all existing tests
            existing_keywords = set()
            for test in existing_tests:
                test_keywords = self.extract_keywords(f"{test.get('name', '')} {test.get('description', '')}")
                existing_keywords.update(test_keywords)
            
            # Find coverage gaps
            new_coverage = new_keywords - existing_keywords
            overlapping_coverage = new_keywords.intersection(existing_keywords)
            
            return {
                'new_coverage_areas': list(new_coverage),
                'overlapping_areas': list(overlapping_coverage),
                'coverage_improvement': len(new_coverage) / len(new_keywords) if new_keywords else 0,
                'total_existing_tests': len(existing_tests),
                'recommendation': self._generate_coverage_recommendation(new_coverage, overlapping_coverage)
            }
            
        except Exception as e:
            logger.error(f"Error analyzing test coverage: {e}")
            return {
                'new_coverage_areas': [],
                'overlapping_areas': [],
                'coverage_improvement': 0,
                'total_existing_tests': 0,
                'recommendation': 'Unable to analyze coverage'
            }
    
    def _generate_coverage_recommendation(self, new_coverage: set, overlapping_coverage: set) -> str:
        """Generate a recommendation based on coverage analysis"""
        if not new_coverage and not overlapping_coverage:
            return "This test doesn't appear to cover any recognizable testing areas."
        
        if not new_coverage:
            return "This test appears to duplicate existing coverage. Consider updating existing tests instead."
        
        if len(new_coverage) > len(overlapping_coverage):
            return "This test adds significant new coverage areas. Recommended to create as new test."
        
        if len(overlapping_coverage) > len(new_coverage):
            return "This test mostly overlaps with existing coverage. Consider enhancing existing tests."
        
        return "This test adds some new coverage while overlapping with existing tests. Review duplicates before creating."

# Global service instance
duplicate_detection_service = DuplicateDetectionService()
