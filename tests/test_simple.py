"""
Simple Test
========
A simple test to verify the fixture works.
"""

import pytest

class TestSimple:
    """Test class for simple functionality"""
    
    def test_browser_setup(self, browser_setup):
        """
        Test that browser_setup fixture works
        
        Args:
            browser_setup: Browser setup fixture
        """
        page, browser, context, playwright = browser_setup
        assert page is not None
        assert browser is not None
        assert context is not None
        assert playwright is not None
        print("Browser setup fixture works!")

