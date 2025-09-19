import asyncio
import json
import logging
from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional, Union
from datetime import datetime
from pathlib import Path

class BaseTestAgent(ABC):
    """Base class for all test automation agents"""
    
    def __init__(
        self, 
        role,
        name: Optional[str] = None,
        system_message: Optional[str] = None,
        **kwargs
    ):
        self.role = role
        self.name = name or f"{self.role}_agent"
        self.logger = logging.getLogger(f"agent.{self.name}")
        self.config = {"system_message": system_message}
        self.state = {
            "status": "initialized",
            "tasks_completed": 0,
            "errors": 0,
            "last_activity": datetime.now(),
        }
        
        self.logger.info(f"Initialized {self.name} with role {self.role}")
    
    @abstractmethod
    async def process_task(self, task_data: Dict[str, Any]) -> Dict[str, Any]:
        """Process a task assigned to this agent"""
        pass
    
    @abstractmethod
    def get_capabilities(self) -> List[str]:
        """Get list of capabilities this agent provides"""
        pass

    def register_function(self, func, description):
        pass

    def update_state(self, status: str, current_task: Optional[str] = None, error_message: Optional[str] = None):
        self.state["status"] = status
        self.state["last_activity"] = datetime.now().isoformat()
        if current_task:
            self.state["current_task"] = current_task
        if error_message:
            self.state["error_message"] = error_message

    def save_work_artifact(self, filename: str, content: Union[str, Dict, List], file_format: str = "txt") -> str:
        work_dir = Path(f"work_dir/{self.name}")
        work_dir.mkdir(parents=True, exist_ok=True)
        file_path = work_dir / filename
        with open(file_path, "w") as f:
            if file_format == "json":
                json.dump(content, f, indent=2)
            else:
                f.write(content)
        return str(file_path)

