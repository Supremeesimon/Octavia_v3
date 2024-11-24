"""
Octavia's Consciousness System - Core awareness and self-monitoring capabilities
"""

from typing import Dict, List, Optional, Any
from datetime import datetime
import asyncio
from loguru import logger

from .cognitive_load import CognitiveLoadManager
from .task_awareness import TaskAwareness, TaskStatus, TaskPriority
from .abilities_awareness import AbilityAwareness, AbilityType, AbilityStatus
from ..memory.memory_patterns import MemoryPatternTracker
from ..context.context_continuity import ContextContinuityManager

class Consciousness:
    """Core consciousness system for Octavia"""
    
    def __init__(self):
        """Initialize consciousness system"""
        self.cognitive_load = CognitiveLoadManager()
        self.task_awareness = TaskAwareness()
        self.abilities = AbilityAwareness()
        self.memory_patterns = MemoryPatternTracker()
        self.context = ContextContinuityManager()
        self._current_context: Dict[str, Any] = {}
        self._abilities_registered = False
        
    async def initialize(self):
        """Initialize consciousness components asynchronously"""
        if not self._abilities_registered:
            await self._register_abilities()
            self._abilities_registered = True
        
    async def _register_abilities(self):
        """Register core abilities"""
        try:
            # File Management
            await self.abilities.register_ability(
                name="File Navigation",
                description="Navigate and manage filesystem",
                ability_type=AbilityType.ACTION,
                requirements={"filesystem": "read_write"},
                metadata={"domain": "file_management"}
            )
            
            # Pattern Recognition
            await self.abilities.register_ability(
                name="Pattern Recognition",
                description="Identify patterns in user behavior and files",
                ability_type=AbilityType.COGNITIVE,
                requirements={"memory": "pattern_tracking"},
                metadata={"domain": "analysis"}
            )
            
            # Context Awareness
            await self.abilities.register_ability(
                name="Context Awareness",
                description="Maintain and use contextual information",
                ability_type=AbilityType.COGNITIVE,
                requirements={"memory": "context_tracking"},
                metadata={"domain": "awareness"}
            )
            
        except Exception as e:
            logger.error(f"Error registering abilities: {e}")
            
    async def process_input(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Process input through consciousness system"""
        try:
            # Update cognitive load
            await self.cognitive_load.update_load(input_data)
            
            # Track context
            context_id = await self.context.add_context(
                "user_input",
                {"content": input_data, "timestamp": datetime.now().isoformat()}
            )
            
            # Update memory patterns
            await self.memory_patterns.track_interaction(
                "input_processing",
                {"type": input_data.get("type"), "context_id": context_id}
            )
            
            # Create task
            task_id = await self.task_awareness.create_task(
                name="Process Input",
                description="Process user input and generate response",
                priority=TaskPriority.HIGH,
                metadata={"context_id": context_id}
            )
            
            # Process with abilities
            processing_result = await self._process_with_abilities(input_data)
            
            # Update task status
            await self.task_awareness.update_task_status(
                task_id,
                TaskStatus.COMPLETED if processing_result else TaskStatus.FAILED
            )
            
            return {
                "result": processing_result,
                "context_id": context_id,
                "task_id": task_id
            }
            
        except Exception as e:
            logger.error(f"Error in consciousness processing: {e}")
            return {"error": str(e)}
            
    async def _process_with_abilities(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Process input using registered abilities"""
        try:
            # Get relevant patterns
            patterns = await self.memory_patterns.get_relevant_patterns(
                "input_processing",
                {"type": data.get("type")}
            )
            
            # Get active contexts
            contexts = self.context.get_active_contexts()
            
            # Combine with current input
            processing_context = {
                "input": data,
                "patterns": patterns,
                "contexts": contexts,
                "cognitive_load": await self.cognitive_load.get_current_load()
            }
            
            # Use abilities based on context
            if "file_operation" in data.get("type", ""):
                return await self.abilities.use_ability("File Navigation", processing_context)
            elif "pattern_analysis" in data.get("type", ""):
                return await self.abilities.use_ability("Pattern Recognition", processing_context)
            else:
                return await self.abilities.use_ability("Context Awareness", processing_context)
                
        except Exception as e:
            logger.error(f"Error in ability processing: {e}")
            return {}
