"""
Octavia's Tool System - Manages and coordinates tool usage
"""

from typing import Dict, List, Optional, Any, Callable
from enum import Enum
import asyncio
from loguru import logger
import threading

from ..awareness.consciousness import Consciousness

class ToolCategory(Enum):
    """Categories of tools"""
    SYSTEM = "system"
    FILE = "file"
    FILE_SYSTEM = "file_system"  # Added for file operations
    NETWORK = "network"
    PROCESS = "process"
    MEMORY = "memory"
    CONTEXT = "context"
    UI = "ui"

class ToolParameter:
    """Tool parameter definition"""
    def __init__(self, name: str, param_type: str, description: str, required: bool = True):
        self.name = name
        self.param_type = param_type
        self.description = description
        self.required = required

class ToolSystem:
    """Manages tool registration and execution"""
    _instance = None
    _initialized = False
    _lock = threading.Lock()
    
    def __new__(cls):
        with cls._lock:
            if cls._instance is None:
                cls._instance = super().__new__(cls)
            return cls._instance
    
    def __init__(self):
        with self._lock:
            if not ToolSystem._initialized:
                self.tools: Dict[str, Dict[str, Any]] = {}
                self.consciousness: Optional[Consciousness] = None
                self._registered_tools = set()  # Track registered tools
                ToolSystem._initialized = True
            
    async def initialize(self):
        """Initialize tool system asynchronously"""
        with self._lock:
            if not self.consciousness:
                self.consciousness = Consciousness()
                await self.consciousness.initialize()
        
    def register_tool(self, name: str, func: Callable, category: ToolCategory,
                     parameters: List[ToolParameter], description: str):
        """Register a new tool"""
        with self._lock:
            if name in self._registered_tools:
                logger.debug(f"Tool {name} already registered")
                return
                
            try:
                self.tools[name] = {
                    'function': func,
                    'category': category,
                    'parameters': parameters,
                    'description': description
                }
                self._registered_tools.add(name)
                logger.info(f"Registered tool: {name}")
                
            except Exception as e:
                logger.error(f"Error registering tool {name}: {e}")
            
    async def execute_tool(self, name: str, **kwargs) -> Any:
        """Execute a registered tool"""
        if not self.consciousness:
            await self.initialize()
            
        try:
            with self._lock:
                if name not in self.tools:
                    raise ValueError(f"Tool {name} not found")
                    
                tool = self.tools[name]
                
                # Validate parameters
                self._validate_parameters(tool['parameters'], kwargs)
            
            # Execute tool outside lock to prevent deadlocks
            result = await tool['function'](**kwargs)
            
            # Record tool usage
            await self._record_tool_usage(name, True)
            
            return result
            
        except Exception as e:
            logger.error(f"Error executing tool {name}: {e}")
            await self._record_tool_usage(name, False)
            raise
            
    def _validate_parameters(self, parameters: List[ToolParameter], kwargs: Dict[str, Any]):
        """Validate tool parameters"""
        for param in parameters:
            if param.required and param.name not in kwargs:
                raise ValueError(f"Required parameter {param.name} not provided")
                
    async def _record_tool_usage(self, name: str, success: bool):
        """Record tool usage in consciousness"""
        if self.consciousness:
            await self.consciousness.process_input({
                "type": "tool_usage",
                "content": {
                    "tool_name": name,
                    "success": success,
                    "timestamp": asyncio.get_event_loop().time()
                }
            })

def tool(name: str, category: ToolCategory, parameters: List[ToolParameter], description: str):
    """Decorator for registering tools"""
    def decorator(func: Callable) -> Callable:
        async def wrapper(*args, **kwargs) -> Any:
            tool_system = ToolSystem()
            return await tool_system.execute_tool(name, **kwargs)
            
        # Register the tool
        tool_system = ToolSystem()
        tool_system.register_tool(name, func, category, parameters, description)
        
        return wrapper
    return decorator
