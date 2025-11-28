"""
Duplicate Prevention Service for AI Test Automation Platform
Handles detection and prevention of duplicate test suites
"""

import logging
from typing import Dict, Any, List, Optional, Tuple
from uuid import UUID
from database_postgres_full import TestSuite, Application, db
import hashlib
import json
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)

class DuplicatePreventionService:
    """Service for detecting and preventing duplicate test suites"""
    
    @staticmethod
    def check_for_duplicates(
        customer_id: str,
        application_id: str,
        test_name: str,
        test_description: str,
        requirements_data: Optional[Dict] = None
    ) -> Dict[str, Any]:
        """
        Check for potential duplicate test suites
        Returns detection results and recommendations
        """
        try:
            # Get existing test suites for the application
            existing_suites = DuplicatePreventionService._get_existing_suites(
                customer_id, application_id
            )
            
            if not existing_suites:
                return {
                    "has_duplicates": False,
                    "duplicate_type": None,
                    "existing_suites": [],
                    "recommendation": "create_new",
                    "confidence": 100
                }
            
            # Check for exact name matches
            exact_matches = [
                suite for suite in existing_suites 
                if suite['name'].lower().strip() == test_name.lower().strip()
            ]
            
            if exact_matches:
                return {
                    "has_duplicates": True,
                    "duplicate_type": "exact_name",
                    "existing_suites": exact_matches,
                    "recommendation": "update_existing",
                    "confidence": 95,
                    "message": f"Found {len(exact_matches)} test suite(s) with the same name"
                }
            
            # Check for similar names (fuzzy matching)
            similar_matches = DuplicatePreventionService._find_similar_names(
                test_name, existing_suites
            )
            
            if similar_matches:
                return {
                    "has_duplicates": True,
                    "duplicate_type": "similar_name",
                    "existing_suites": similar_matches,
                    "recommendation": "confirm_create",
                    "confidence": 75,
                    "message": f"Found {len(similar_matches)} test suite(s) with similar names"
                }
            
            # Check for similar content based on requirements
            if requirements_data:
                content_matches = DuplicatePreventionService._find_similar_content(
                    requirements_data, existing_suites, customer_id
                )
                
                if content_matches:
                    return {
                        "has_duplicates": True,
                        "duplicate_type": "similar_content",
                        "existing_suites": content_matches,
                        "recommendation": "confirm_create",
                        "confidence": 60,
                        "message": f"Found {len(content_matches)} test suite(s) with similar test content"
                    }
            
            # Check for recent duplicates (same application, recent creation)
            recent_matches = DuplicatePreventionService._find_recent_suites(
                customer_id, application_id, hours=24
            )
            
            if recent_matches:
                return {
                    "has_duplicates": True,
                    "duplicate_type": "recent_creation",
                    "existing_suites": recent_matches,
                    "recommendation": "confirm_create",
                    "confidence": 40,
                    "message": f"Found {len(recent_matches)} test suite(s) created recently for this application"
                }
            
            return {
                "has_duplicates": False,
                "duplicate_type": None,
                "existing_suites": [],
                "recommendation": "create_new",
                "confidence": 100
            }
            
        except Exception as e:
            logger.error(f"Duplicate detection error: {e}")
            return {
                "has_duplicates": False,
                "duplicate_type": "error",
                "existing_suites": [],
                "recommendation": "create_new",
                "confidence": 0,
                "error": str(e)
            }
    
    @staticmethod
    def _get_existing_suites(customer_id: str, application_id: str) -> List[Dict]:
        """Get existing test suites for the application"""
        try:
            query = """
            SELECT ts.id, ts.name, ts.description, ts.created_at, ts.status,
                   ts.test_type, ts.created_by
            FROM test_suites ts
            WHERE ts.customer_id = %s AND ts.application_id = %s
            ORDER BY ts.created_at DESC
            """
            
            result = db.execute_query(query, (customer_id, application_id))
            return [dict(row) for row in result] if result else []
            
        except Exception as e:
            logger.error(f"Error fetching existing suites: {e}")
            return []
    
    @staticmethod
    def _find_similar_names(test_name: str, existing_suites: List[Dict]) -> List[Dict]:
        """Find test suites with similar names using simple string similarity"""
        similar_matches = []
        test_name_lower = test_name.lower().strip()
        test_words = set(test_name_lower.split())
        
        for suite in existing_suites:
            suite_name_lower = suite['name'].lower().strip()
            suite_words = set(suite_name_lower.split())
            
            # Calculate word overlap
            common_words = test_words.intersection(suite_words)
            total_words = test_words.union(suite_words)
            
            if len(total_words) > 0:
                similarity = len(common_words) / len(total_words)
                
                # Consider it similar if > 60% word overlap
                if similarity > 0.6:
                    suite_copy = suite.copy()
                    suite_copy['similarity_score'] = round(similarity * 100, 1)
                    similar_matches.append(suite_copy)
        
        return similar_matches
    
    @staticmethod
    def _find_similar_content(
        requirements_data: Dict, 
        existing_suites: List[Dict], 
        customer_id: str
    ) -> List[Dict]:
        """Find test suites with similar content based on requirements"""
        # This is a simplified implementation
        # In a real system, you might store test content hashes or use ML for similarity
        
        content_matches = []
        
        # Create a simple content signature from requirements
        content_signature = DuplicatePreventionService._create_content_signature(
            requirements_data
        )
        
        # For now, just return suites created in the last week as potential content matches
        # In a real implementation, you would compare actual test content
        recent_cutoff = datetime.now() - timedelta(days=7)
        
        for suite in existing_suites:
            if suite['created_at'] > recent_cutoff:
                suite_copy = suite.copy()
                suite_copy['content_similarity'] = "potential_match"
                content_matches.append(suite_copy)
        
        return content_matches[:3]  # Limit to top 3 matches
    
    @staticmethod
    def _find_recent_suites(customer_id: str, application_id: str, hours: int = 24) -> List[Dict]:
        """Find test suites created recently"""
        try:
            cutoff_time = datetime.now() - timedelta(hours=hours)
            
            query = """
            SELECT ts.id, ts.name, ts.description, ts.created_at, ts.status
            FROM test_suites ts
            WHERE ts.customer_id = %s AND ts.application_id = %s 
            AND ts.created_at > %s
            ORDER BY ts.created_at DESC
            """
            
            result = db.execute_query(query, (customer_id, application_id, cutoff_time))
            return [dict(row) for row in result] if result else []
            
        except Exception as e:
            logger.error(f"Error fetching recent suites: {e}")
            return []
    
    @staticmethod
    def _create_content_signature(requirements_data: Dict) -> str:
        """Create a signature for requirements content"""
        try:
            # Extract key elements for signature
            signature_data = {
                "categories": [],
                "test_count": 0
            }
            
            test_categories = requirements_data.get('testCategories', [])
            for category in test_categories:
                category_info = {
                    "name": category.get('category', '').lower(),
                    "test_count": len(category.get('tests', []))
                }
                signature_data["categories"].append(category_info)
                signature_data["test_count"] += category_info["test_count"]
            
            # Create hash of signature
            signature_json = json.dumps(signature_data, sort_keys=True)
            return hashlib.md5(signature_json.encode()).hexdigest()
            
        except Exception as e:
            logger.error(f"Error creating content signature: {e}")
            return ""
    
    @staticmethod
    def suggest_update_strategy(
        existing_suite_id: str,
        new_requirements: Optional[Dict] = None
    ) -> Dict[str, Any]:
        """Suggest how to update an existing test suite"""
        try:
            # Get existing suite details
            query = """
            SELECT ts.*, app.name as application_name
            FROM test_suites ts
            JOIN applications app ON ts.application_id = app.id
            WHERE ts.id = %s
            """
            
            result = db.execute_query(query, (existing_suite_id,))
            result = result[0] if result else None
            if not result:
                return {
                    "strategy": "create_new",
                    "reason": "Existing suite not found"
                }
            
            existing_suite = dict(result)
            
            # Determine update strategy based on suite status
            if existing_suite['status'] == 'running':
                return {
                    "strategy": "wait_or_create_new",
                    "reason": "Existing suite is currently running",
                    "recommendation": "Wait for completion or create a new suite"
                }
            
            if existing_suite['status'] == 'failed':
                return {
                    "strategy": "replace",
                    "reason": "Existing suite failed, safe to replace",
                    "recommendation": "Update the existing suite with new configuration"
                }
            
            if existing_suite['status'] == 'completed':
                return {
                    "strategy": "version_or_replace",
                    "reason": "Existing suite completed successfully",
                    "recommendation": "Create new version or replace if significantly different"
                }
            
            return {
                "strategy": "update",
                "reason": "Safe to update existing suite",
                "recommendation": "Update the existing suite with new configuration"
            }
            
        except Exception as e:
            logger.error(f"Error suggesting update strategy: {e}")
            return {
                "strategy": "create_new",
                "reason": f"Error analyzing existing suite: {str(e)}"
            }
