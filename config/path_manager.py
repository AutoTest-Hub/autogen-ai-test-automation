"""
Path Manager
===========
Centralized path management for the AutoGen AI Test Automation Framework.
"""

import os
import logging
from pathlib import Path
from typing import Optional, List

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class PathManager:
    """Centralized path management for the framework"""
    
    def __init__(self):
        """Initialize path manager"""
        # Project root directory (parent of config directory)
        self.project_root = Path(__file__).parent.parent.absolute()
        
        # Standard directories
        self.work_dir = self.project_root / "work_dir"
        self.tests_dir = self.project_root / "tests"
        self.pages_dir = self.project_root / "pages"
        self.utils_dir = self.project_root / "utils"
        self.config_dir = self.project_root / "config"
        self.screenshots_dir = self.project_root / "screenshots"
        self.templates_dir = self.project_root / "templates"
        
        # Create directories if they don't exist
        self._create_directories()
        
        logger.info("Path manager initialized. Project root: {}".format(self.project_root))
    
    def _create_directories(self):
        """Create necessary directories if they don't exist"""
        directories = [
            self.work_dir,
            self.tests_dir,
            self.pages_dir,
            self.utils_dir,
            self.screenshots_dir,
            self.templates_dir
        ]
        
        for directory in directories:
            directory.mkdir(parents=True, exist_ok=True)
            logger.debug("Directory ensured: {}".format(directory))
    
    def get_agent_work_dir(self, agent_name: str) -> Path:
        """Get the work directory for a specific agent"""
        agent_work_dir = self.work_dir / agent_name
        agent_work_dir.mkdir(parents=True, exist_ok=True)
        return agent_work_dir
    
    def get_latest_file(self, directory: Path, pattern: str) -> Optional[Path]:
        """Get the latest file matching a pattern in a directory"""
        try:
            files = list(directory.glob(pattern))
            if not files:
                return None
            
            # Sort by modification time, newest first
            return sorted(files, key=lambda f: f.stat().st_mtime, reverse=True)[0]
        except Exception as e:
            logger.error("Error finding latest file with pattern {} in {}: {}".format(
                pattern, directory, str(e)
            ))
            return None
    
    def find_files(self, directory: Path, pattern: str) -> List[Path]:
        """Find all files matching a pattern in a directory"""
        try:
            return list(directory.glob(pattern))
        except Exception as e:
            logger.error("Error finding files with pattern {} in {}: {}".format(
                pattern, directory, str(e)
            ))
            return []
    
    def find_file_in_directories(self, directories: List[Path], pattern: str) -> Optional[Path]:
        """Find a file matching a pattern in multiple directories"""
        for directory in directories:
            if not directory.exists():
                continue
                
            latest = self.get_latest_file(directory, pattern)
            if latest:
                return latest
        
        return None
    
    def get_discovery_results(self) -> Optional[Path]:
        """Get the latest discovery results file"""
        # Check in multiple possible locations
        locations = [
            self.work_dir / "RealBrowserDiscoveryAgent",
            self.work_dir / "RealDiscoveryIntegration",
            self.work_dir / "DiscoveryAgent"
        ]
        
        # First try to find files with the exact pattern
        result = self.find_file_in_directories(locations, "discovery_results_*.json")
        if result:
            logger.info("Found discovery results: {}".format(result))
            return result
            
        # If not found, try a broader search
        for location in locations:
            if not location.exists():
                continue
                
            # Try to find any JSON file that might contain discovery results
            json_files = self.find_files(location, "*.json")
            if json_files:
                logger.info("Found potential discovery results: {}".format(json_files[0]))
                return json_files[0]
        
        logger.warning("No discovery results found in any expected location")
        return None
    
    def ensure_file_directory(self, file_path: Path) -> None:
        """Ensure the directory for a file exists"""
        file_path.parent.mkdir(parents=True, exist_ok=True)
    
    def normalize_path(self, path: str) -> Path:
        """Normalize a path string to a Path object"""
        if isinstance(path, Path):
            return path
            
        # Convert to absolute path if not already
        if not os.path.isabs(path):
            path = os.path.join(str(self.project_root), path)
            
        return Path(path)

# Create global path manager instance
path_manager = PathManager()

