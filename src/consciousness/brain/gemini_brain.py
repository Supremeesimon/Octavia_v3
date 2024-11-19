"""
Octavia's Gemini-powered Brain
"""

import os
from typing import Dict, List, Optional
from loguru import logger
import vertexai
from vertexai.preview.generative_models import GenerativeModel, ChatSession
from vertexai.preview.language_models import ChatModel

class GeminiBrain:
    """Brain powered by Google's Gemini Flash API"""
    
    def __init__(self):
        """Initialize the Gemini brain"""
        try:
            # Initialize Vertex AI
            project_id = os.getenv("GOOGLE_CLOUD_PROJECT")
            location = os.getenv("GOOGLE_CLOUD_LOCATION", "us-central1")
            
            if not project_id:
                raise ValueError("GOOGLE_CLOUD_PROJECT environment variable not set")
            
            vertexai.init(project=project_id, location=location)
            
            # Initialize Gemini model
            self.model = GenerativeModel("gemini-pro")
            self.chat = self.model.start_chat()
            logger.info("Successfully initialized Gemini brain")
            
        except Exception as e:
            logger.error(f"Failed to initialize Gemini brain: {e}")
            raise

    async def think(self, message: str, context: Dict, history: List[Dict]) -> str:
        """
        Process a message with context and history to generate a response
        
        Args:
            message: The user's message
            context: Current system context and user preferences
            history: Recent conversation history
            
        Returns:
            Octavia's response
        """
        try:
            # Format context and history for the model
            formatted_context = self._format_context(context)
            formatted_history = self._format_history(history)
            
            # Combine everything into a prompt
            prompt = f"{formatted_context}\n\n{formatted_history}\nUser: {message}\nOctavia:"
            
            # Get response from Gemini
            response = self.chat.send_message(prompt)
            
            return response.text
            
        except Exception as e:
            logger.error(f"Error in think: {e}")
            return "I apologize, but I'm having trouble processing that right now. Could you try again?"

    def _format_context(self, context: Dict) -> str:
        """Format context for the model"""
        try:
            system_state = context.get('system_state', {})
            user_prefs = context.get('user_preferences', {})
            
            context_str = "Current Context:\n"
            
            if system_state:
                context_str += f"System State: {system_state}\n"
            
            if user_prefs:
                context_str += f"User Preferences: {user_prefs}\n"
            
            return context_str
        except Exception as e:
            logger.error(f"Error formatting context: {e}")
            return ""

    def _format_history(self, history: List[Dict]) -> str:
        """Format conversation history for the model"""
        try:
            if not history:
                return ""
            
            history_str = "Recent Conversation:\n"
            
            for entry in history:
                user_msg = entry.get('user', '')
                assistant_msg = entry.get('assistant', '')
                
                if user_msg:
                    history_str += f"User: {user_msg}\n"
                if assistant_msg:
                    history_str += f"Octavia: {assistant_msg}\n"
            
            return history_str
        except Exception as e:
            logger.error(f"Error formatting history: {e}")
            return ""
