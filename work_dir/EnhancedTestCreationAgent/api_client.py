"""
API Client for Test Automation
==============================
"""

import requests
import json
import logging

logger = logging.getLogger(__name__)

class APIClient:
    """API client for test automation"""
    
    def __init__(self, base_url: str):
        self.base_url = base_url.rstrip('/')
        self.session = requests.Session()
        self.session.headers.update({
            'Content-Type': 'application/json',
            'User-Agent': 'AutoGen-Test-Framework/1.0'
        })
    
    def get(self, endpoint: str, params=None, **kwargs):
        """Make GET request"""
        url = f"{self.base_url}{endpoint}"
        logger.info(f"GET {url}")
        
        try:
            response = self.session.get(url, params=params, **kwargs)
            logger.info(f"Response: {response.status_code}")
            return response
        except Exception as e:
            logger.error(f"GET request failed: {str(e)}")
            raise
    
    def post(self, endpoint: str, data=None, json=None, **kwargs):
        """Make POST request"""
        url = f"{self.base_url}{endpoint}"
        logger.info(f"POST {url}")
        
        try:
            response = self.session.post(url, data=data, json=json, **kwargs)
            logger.info(f"Response: {response.status_code}")
            return response
        except Exception as e:
            logger.error(f"POST request failed: {str(e)}")
            raise
