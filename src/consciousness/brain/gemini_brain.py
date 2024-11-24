"""
Octavia's Gemini-powered Brain using direct API access
"""

import os
import re
from typing import Dict, List, Optional
from loguru import logger
import asyncio

from .modules import CommandProcessor, ConversationManager, ModelManager
from .prompt_manager import PromptManager

class GeminiBrain:
    """Brain powered by Google's Gemini API"""
    
    def __init__(self, api_key: str = None):
        """Initialize the Gemini brain with an API key."""
        try:
            logger.info("Initializing Gemini brain...")
            
            # Initialize components in correct order
            self.model_manager = ModelManager(api_key)
            self.conversation_manager = ConversationManager(self)
            self.command_processor = CommandProcessor(self, self.conversation_manager)
            self.prompt_manager = PromptManager()
            
            logger.info("Successfully initialized Gemini brain")
            
        except Exception as e:
            logger.error(f"Error initializing Gemini brain: {str(e)}")
            raise

    async def set_api_key(self, api_key: str) -> bool:
        """Set or update the Gemini API key."""
        try:
            logger.info("Updating Gemini API key...")
            if not api_key or len(api_key.strip()) < 10:  # Basic validation
                logger.error("Invalid API key format")
                return False
                
            # Update the API key in the model manager
            self.model_manager.api_key = api_key
            
            # Test the key with a simple query
            test_response = await self.model_manager.generate_text("Test connection")
            if test_response:
                logger.info("API key validated successfully")
                return True
            else:
                logger.error("API key validation failed - no response")
                return False
                
        except Exception as e:
            logger.error(f"Error setting API key: {str(e)}")
            return False

    def _enrich_context(self, context: Dict) -> Dict:
        """Enrich context with additional information"""
        if not context:
            return {}
            
        # Only copy if we're going to modify
        enriched = context
        
        # Add user technical level if available
        if hasattr(self.conversation_manager, '_user_style'):
            enriched = context.copy()
            enriched['user_technical_level'] = self.conversation_manager._user_style.get('technical', 0.5)
        
        return enriched

    async def generate_response(self, message: str, context: Optional[Dict] = None) -> str:
        """Generate a response using the Gemini model"""
        try:
            if not self.model_manager.model:
                raise ValueError("Model not initialized. Please set API key first.")
            
            # Get context-aware prompt
            system_prompt = self.prompt_manager.get_prompt(self._enrich_context(context or {}))
            
            # Build full prompt
            full_prompt = f"{system_prompt}\n\nUser: {message}\n\nAssistant:"
            
            # Generate response
            return (await self.model_manager.generate_response(full_prompt)).strip()
            
        except Exception as e:
            logger.error(f"Error generating response: {str(e)}")
            raise

    async def think(self, message: str, context: Dict, history: List[Dict]) -> str:
        """Process a message with context and history to generate a response"""
        try:
            # Enrich context with additional information
            enriched_context = self._enrich_context(context)
            
            # Build the prompt
            prompt = f"{self.prompt_manager.get_prompt(enriched_context)}\n\n"
            
            # Add context if available
            if enriched_context:
                prompt += f"{self.conversation_manager.format_context(enriched_context)}\n"
            
            # Add conversation history
            if history:
                prompt += f"{self.conversation_manager.format_history(history)}\n"
            
            # Add the current message
            prompt += f"User: {message}\nOctavia:"
            
            # Generate and process response
            response = await self.model_manager.generate_response(prompt)
            
            # Execute any commands in the response
            if "```" in response:
                blocks = response.split("```")
                for i in range(1, len(blocks), 2):
                    if blocks[i].startswith(("shell", "bash")):
                        command = blocks[i].split("\n", 1)[1].strip()
                        result = await self.command_processor.execute_command(command)
                        if result["success"]:
                            response = response.replace(
                                f"```{blocks[i]}```",
                                f"\n{result['output']}\n"
                            )
                        else:
                            response = response.replace(
                                f"```{blocks[i]}```",
                                f"\n{result['output']}\n"
                            )
            
            # Store in history
            self.conversation_manager.add_to_history(message, response)
            
            return response
            
        except Exception as e:
            error_msg = str(e)
            logger.error(f"Error in think: {error_msg}")
            return f"I hit a small snag while processing that. Could you try again? \nTechnical details: {error_msg}"

    async def process_message(self, message: str) -> str:
        """Process a message and return the response"""
        try:
            return await self.think(message, {}, [])
        except Exception as e:
            return f"I apologize, but something went wrong: {str(e)}"

    async def test_connection(self) -> bool:
        """Test the API connection with a simple query."""
        return await self.model_manager.test_connection()

    def clear_conversation(self):
        """Clear the conversation history and reset the chat session."""
        self.conversation_manager.clear_history()
        self.prompt_manager.clear_cache()

    def request_stop(self):
        """Request to stop the current response generation"""
        self.model_manager.request_stop()
