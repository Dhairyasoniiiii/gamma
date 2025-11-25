"""
Base Agent class for all AI agents
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, List
import asyncio
from datetime import datetime


class BaseAgent(ABC):
    """Base class for all AI agents"""
    
    def __init__(self, name: str):
        self.name = name
        self.tasks = []
        self.is_running = False
    
    @abstractmethod
    async def process(self, input_data: Dict) -> Dict:
        """Process input and return result"""
        pass
    
    async def start(self):
        """Start the agent"""
        self.is_running = True
        print(f"[Agent {self.name}] Started")
        
        while self.is_running:
            if self.tasks:
                task = self.tasks.pop(0)
                try:
                    result = await self.process(task)
                    await self.on_success(result)
                except Exception as e:
                    await self.on_error(task, e)
            else:
                await asyncio.sleep(1)
    
    async def add_task(self, task: Dict):
        """Add task to queue"""
        self.tasks.append(task)
    
    async def on_success(self, result: Dict):
        """Handle successful task"""
        print(f"[Agent {self.name}] Task completed successfully")
    
    async def on_error(self, task: Dict, error: Exception):
        """Handle failed task"""
        print(f"[Agent {self.name}] Task failed: {str(error)}")
    
    def stop(self):
        """Stop the agent"""
        self.is_running = False
        print(f"[Agent {self.name}] Stopped")
