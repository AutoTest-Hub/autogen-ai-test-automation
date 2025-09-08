"""
Compatibility Utilities
======================
Utilities for ensuring compatibility across different Python versions.
"""

import sys
import logging
from typing import Dict, Any, Callable, Optional

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class CompatibilityHelper:
    """Helper for ensuring compatibility across different Python versions"""
    
    def __init__(self):
        """Initialize compatibility helper"""
        self.python_version = sys.version_info
        self.major = self.python_version.major
        self.minor = self.python_version.minor
        
        # Python 2 or Python 3 before 3.6 needs compatible syntax
        self.needs_compatible_syntax = (self.major == 2) or (self.major == 3 and self.minor < 6)
        
        logger.info("Compatibility helper initialized. Python version: {}.{}".format(
            self.major, self.minor
        ))
        
        if self.needs_compatible_syntax:
            logger.info("Using compatible syntax for Python {}.{}".format(self.major, self.minor))
    
    def format_string(self, template: str, **kwargs) -> str:
        """Format a string in a version-compatible way"""
        if self.needs_compatible_syntax:
            return template.format(**kwargs)
        else:
            # Use eval to avoid syntax errors in Python < 3.6
            # This allows f-strings in the code while still supporting older Python versions
            locals().update(kwargs)
            return eval('f"""' + template + '"""')
    
    def get_compatible_function(self, modern_func: Callable, compat_func: Callable) -> Callable:
        """Get the appropriate function based on Python version"""
        if self.needs_compatible_syntax:
            return compat_func
        else:
            return modern_func
    
    def is_python2(self) -> bool:
        """Check if running on Python 2"""
        return self.major == 2
    
    def is_python3(self) -> bool:
        """Check if running on Python 3"""
        return self.major == 3
    
    def supports_async(self) -> bool:
        """Check if Python version supports async/await syntax"""
        return (self.major == 3 and self.minor >= 5)
    
    def supports_f_strings(self) -> bool:
        """Check if Python version supports f-strings"""
        return (self.major == 3 and self.minor >= 6)
    
    def supports_type_hints(self) -> bool:
        """Check if Python version supports type hints"""
        return (self.major == 3 and self.minor >= 5)
    
    def get_version_info(self) -> Dict[str, Any]:
        """Get Python version information"""
        return {
            "major": self.major,
            "minor": self.minor,
            "micro": self.python_version.micro,
            "releaselevel": self.python_version.releaselevel,
            "serial": self.python_version.serial,
            "needs_compatible_syntax": self.needs_compatible_syntax,
            "supports_async": self.supports_async(),
            "supports_f_strings": self.supports_f_strings(),
            "supports_type_hints": self.supports_type_hints()
        }

# Create global compatibility helper instance
compatibility_helper = CompatibilityHelper()

