"""
Octavia's Conversation Handler
"""

from typing import Optional, Dict
from loguru import logger

from ..brain.gemini_brain import GeminiBrain
from ..context.context_manager import ContextManager

class ConversationHandler:
    """Manages conversations between user and Octavia"""
    
    def __init__(self):
        """Initialize conversation handler with brain and context"""
        self.brain = GeminiBrain()
        self.context = ContextManager()
        logger.info("Initialized Conversation Handler")

    async def process_message(self, message: str) -> str:
        """
        Process a user message and return Octavia's response
        
        Args:
            message: The user's message
            
        Returns:
            Octavia's response
        """
        try:
            # Get current context and history
            context = await self.context.get_current_context()
            history = await self.context.get_recent_history()
            
            # Get response from brain
            response = await self.brain.think(message, context, history)
            
            # Store the conversation
            await self.context.add_conversation_entry(message, response)
            
            # Update system state if needed
            await self._update_system_state(message, response)
            
            return response
        except Exception as e:
            logger.error(f"Error processing message: {e}")
            return "I'm having trouble processing that right now. Could you try again?"

    async def _update_system_state(self, message: str, response: str):
        """Update system state based on conversation"""
        try:
            # Get current state
            context = await self.context.get_current_context()
            current_state = context.get('system_state', {})
            
            # Update state based on conversation
            # TODO: Implement state updates based on conversation content
            # For example:
            # - Track user's current task
            # - Note user's mood
            # - Record important information
            
            # For now, just update last_interaction
            current_state['last_interaction'] = {
                'user_message': message,
                'assistant_response': response
            }
            
            await self.context.update_system_state(current_state)
        except Exception as e:
            logger.error(f"Error updating system state: {e}")

    async def update_user_preferences(self, preferences: Dict):
        """Update user preferences"""
        try:
            await self.context.update_user_preferences(preferences)
            logger.info("Successfully updated user preferences")
        except Exception as e:
            logger.error(f"Error updating user preferences: {e}")
            raise
