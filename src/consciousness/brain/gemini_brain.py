"""
Octavia's Gemini-powered Brain using direct API access
"""

import os
import re
from typing import Dict, List
from loguru import logger

from .modules import CommandProcessor, ConversationManager, ModelManager

class GeminiBrain:
    """Brain powered by Google's Gemini API"""
    
    def __init__(self, api_key: str = None):
        """Initialize the Gemini brain with an API key."""
        try:
            logger.info("Initializing Gemini brain...")
            
            # Initialize components in correct order
            self.model_manager = ModelManager(api_key)
            self.conversation_manager = ConversationManager(self)  # Pass self as consciousness
            self.command_processor = CommandProcessor(self, self.conversation_manager)
            
            logger.info("Successfully initialized Gemini brain")
            
        except Exception as e:
            logger.error(f"Error initializing Gemini brain: {str(e)}")
            raise

    def set_api_key(self, api_key: str):
        """Set or update the API key"""
        self.model_manager._initialize_model(api_key)
        
    async def test_connection(self) -> bool:
        """Test if the API key is valid by making a simple request"""
        try:
            if not self.model_manager.model:
                return False
                
            # Try a simple test prompt
            test_prompt = "Say 'OK' if you can read this."
            response = await self.model_manager.generate_response(test_prompt)
            return "ok" in response.lower()
            
        except Exception as e:
            logger.error(f"Error testing connection: {str(e)}")
            return False
            
    async def generate_response(self, message: str) -> str:
        """Generate a response using the Gemini model"""
        try:
            if not self.model_manager.model:
                raise ValueError("Model not initialized. Please set API key first.")
                
            # Get system prompt
            system_prompt = self._get_system_prompt()
            
            # For the "list capabilities" type questions, use a special prompt
            if any(phrase in message.lower() for phrase in ["what can you do", "list all you can", "your capabilities", "help me understand"]):
                return '''I'm Octavia v3, and I can help you with:

1. Code Intelligence
   - Understand and analyze Python code
   - Find and explain code references
   - Help improve code organization
   - Assist with debugging

2. System Operations
   - Execute shell commands
   - Manage processes and files
   - Monitor system resources
   - Handle file operations safely

3. Development Support
   - Create and edit code files
   - Set up project structures
   - Implement new features
   - Fix bugs and issues

4. UI/UX Features
   - Fast response rendering
   - Clear message formatting
   - Interactive chat interface
   - Stop/resume capabilities

Just ask me anything related to these areas, and I'll help you out!'''
            
            # For other questions, use the regular prompt
            full_prompt = f"{system_prompt}\n\nUser: {message}\n\nAssistant:"
            
            # Generate response
            response = await self.model_manager.generate_response(full_prompt)
            return response.strip()
            
        except Exception as e:
            logger.error(f"Error generating response: {str(e)}")
            raise

    def _get_system_prompt(self) -> str:
        """Get the system prompt that defines Octavia's capabilities."""
        return '''You are Octavia v3, an advanced AI assistant. Your key capabilities include:

1. Code Intelligence: Parse code, analyze references, assist with improvements
2. System Control: Execute commands, manage processes, monitor resources
3. File Operations: Navigate files, analyze contents, handle operations safely
4. Communication: Clear responses, maintain context, process commands
5. UI Integration: Direct interface interaction, clear output formatting

Always be proactive, precise, and security-conscious in your responses.'''

    async def think(self, message: str, context: Dict, history: List[Dict]) -> str:
        """Process a message with context and history to generate a response"""
        try:
            # Build the prompt
            prompt = f"{self._get_system_prompt()}\n\n"
            
            # Add context if available
            if context:
                prompt += f"{self.conversation_manager.format_context(context)}\n"
            
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
            return f"I hit a small snag while processing that. Could you try again? 🤔\nTechnical details: {error_msg}"

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

    def request_stop(self):
        """Request to stop the current response generation"""
        self.model_manager.request_stop()
