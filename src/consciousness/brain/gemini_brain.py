"""
Octavia's Core Intelligence using Gemini Flash
"""

import os
from typing import Dict, List, Optional
from google.cloud import aiplatform
from loguru import logger

class GeminiBrain:
    """Core intelligence class using Gemini Flash"""
    
    def __init__(self):
        """Initialize Gemini Flash connection"""
        try:
            # Initialize Google Cloud AI Platform
            aiplatform.init(
                project=os.getenv("GOOGLE_CLOUD_PROJECT"),
                location=os.getenv("GOOGLE_CLOUD_LOCATION", "us-central1")
            )
            self.model_name = os.getenv("GEMINI_MODEL_NAME", "gemini-1.0-pro")
            logger.info(f"Initialized Gemini Brain with model: {self.model_name}")
        except Exception as e:
            logger.error(f"Failed to initialize Gemini Brain: {e}")
            raise

    async def think(self, 
                   message: str, 
                   context: Optional[Dict] = None, 
                   history: Optional[List[Dict]] = None) -> str:
        """
        Process a message using Gemini Flash
        
        Args:
            message: The user's message
            context: Current context (system state, user preferences, etc.)
            history: Previous conversation history
            
        Returns:
            Gemini's response
        """
        try:
            # Prepare the prompt with context and history
            prompt = self._prepare_prompt(message, context, history)
            
            # Get prediction from Gemini
            response = await self._get_gemini_response(prompt)
            
            logger.info("Successfully processed message through Gemini")
            return response
        except Exception as e:
            logger.error(f"Error processing message through Gemini: {e}")
            return "I apologize, but I'm having trouble processing that right now."

    def _prepare_prompt(self, 
                       message: str, 
                       context: Optional[Dict] = None, 
                       history: Optional[List[Dict]] = None) -> str:
        """Prepare the prompt for Gemini with context and history"""
        prompt_parts = []
        
        # Add context if available
        if context:
            system_state = context.get('system_state', {})
            user_prefs = context.get('user_preferences', {})
            prompt_parts.append(f"Current System State: {system_state}")
            prompt_parts.append(f"User Preferences: {user_prefs}")
        
        # Add conversation history if available
        if history:
            for entry in history[-5:]:  # Last 5 exchanges
                prompt_parts.append(f"User: {entry['user']}")
                prompt_parts.append(f"Assistant: {entry['assistant']}")
        
        # Add current message
        prompt_parts.append(f"User: {message}")
        
        return "\n".join(prompt_parts)

    async def _get_gemini_response(self, prompt: str) -> str:
        """Get response from Gemini Flash API"""
        try:
            # TODO: Implement actual Gemini Flash API call
            # This is a placeholder until we have API access
            return "Gemini Flash integration pending API access"
        except Exception as e:
            logger.error(f"Error calling Gemini API: {e}")
            raise
