"""
Octavia's Cognitive Load Management System
"""

from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from enum import Enum
import psutil
import time
from loguru import logger

class ComplexityLevel(Enum):
    """Task complexity levels"""
    TRIVIAL = 1
    SIMPLE = 2
    MODERATE = 3
    COMPLEX = 4
    VERY_COMPLEX = 5

@dataclass
class SystemLoad:
    """System resource usage metrics"""
    cpu_percent: float
    memory_percent: float
    disk_io: float
    active_tasks: int

@dataclass
class UserLoad:
    """User cognitive load indicators"""
    task_complexity: ComplexityLevel
    context_switches: int
    error_rate: float
    response_time: float
    task_stack_depth: int

class CognitiveLoadManager:
    """Manages system and user cognitive load"""
    
    def __init__(self):
        self._system_load = SystemLoad(0.0, 0.0, 0.0, 0)
        self._user_load = UserLoad(
            ComplexityLevel.SIMPLE,
            0,
            0.0,
            0.0,
            0
        )
        self._task_stack: List[Dict[str, Any]] = []
        self._last_update = time.time()
        
    async def update_system_load(self):
        """Update system load metrics"""
        try:
            cpu = psutil.cpu_percent(interval=0.1)
            memory = psutil.virtual_memory().percent
            disk = psutil.disk_io_counters()
            disk_io = (disk.read_bytes + disk.write_bytes) / 1024 / 1024  # MB
            
            self._system_load = SystemLoad(
                cpu_percent=cpu,
                memory_percent=memory,
                disk_io=disk_io,
                active_tasks=len(self._task_stack)
            )
        except Exception as e:
            logger.error(f"Error updating system load: {e}")
            
    async def update_user_load(self, 
                             complexity: Optional[ComplexityLevel] = None,
                             context_switch: bool = False,
                             error_occurred: bool = False,
                             response_time: Optional[float] = None):
        """Update user cognitive load metrics"""
        try:
            if complexity:
                self._user_load.task_complexity = complexity
                
            if context_switch:
                self._user_load.context_switches += 1
                
            if error_occurred:
                self._user_load.error_rate = (
                    self._user_load.error_rate * 0.9 + 0.1
                )
            
            if response_time:
                self._user_load.response_time = (
                    self._user_load.response_time * 0.9 + response_time * 0.1
                )
                
            self._user_load.task_stack_depth = len(self._task_stack)
            
        except Exception as e:
            logger.error(f"Error updating user load: {e}")
            
    def push_task(self, task: Dict[str, Any]):
        """Add task to stack"""
        self._task_stack.append(task)
        
    def pop_task(self) -> Optional[Dict[str, Any]]:
        """Remove and return top task"""
        return self._task_stack.pop() if self._task_stack else None
        
    def get_combined_load(self) -> float:
        """Calculate combined cognitive load (0-1)"""
        # System load factors
        system_load = (
            self._system_load.cpu_percent * 0.3 +
            self._system_load.memory_percent * 0.3 +
            min(self._system_load.disk_io / 100, 1.0) * 0.2 +
            min(self._system_load.active_tasks / 5, 1.0) * 0.2
        ) / 100  # Normalize to 0-1
        
        # User load factors
        user_load = (
            self._user_load.task_complexity.value / 5 * 0.3 +
            min(self._user_load.context_switches / 10, 1.0) * 0.2 +
            self._user_load.error_rate * 0.2 +
            min(self._user_load.task_stack_depth / 5, 1.0) * 0.3
        )
        
        # Combine loads with weights
        return system_load * 0.4 + user_load * 0.6
        
    def should_break_task(self) -> bool:
        """Determine if current task should be broken down"""
        combined_load = self.get_combined_load()
        return (combined_load > 0.7 or 
                self._user_load.task_complexity.value >= ComplexityLevel.COMPLEX.value or
                self._user_load.task_stack_depth >= 3)
        
    def get_optimal_chunk_size(self) -> int:
        """Calculate optimal chunk size for information"""
        combined_load = self.get_combined_load()
        base_chunk = 5  # Base chunk size
        
        if combined_load > 0.8:
            return base_chunk
        elif combined_load > 0.6:
            return base_chunk * 2
        elif combined_load > 0.4:
            return base_chunk * 3
        else:
            return base_chunk * 4
            
    def suggest_break(self) -> bool:
        """Suggest if user needs a break"""
        return (self.get_combined_load() > 0.8 or
                self._user_load.error_rate > 0.3 or
                self._user_load.context_switches > 15)
