"""
Octavia's Gemini-powered Brain using direct API access
"""

import os
from typing import Dict, List
import google.generativeai as genai
from loguru import logger
from dotenv import load_dotenv

class GeminiBrain:
    """Brain powered by Google's Gemini API"""
    
    def __init__(self, api_key: str = None):
        """Initialize the Gemini brain with an API key."""
        try:
            logger.info("Initializing Gemini brain...")
            
            # Load API key from environment if not provided
            if not api_key:
                load_dotenv()
                api_key = os.getenv('GEMINI_API_KEY')
            
            if not api_key:
                logger.error("No API key provided!")
                raise ValueError("API key is required")
            
            # Clean and store the key
            self._api_key = api_key.strip()
            
            # Configure the client
            logger.info("Configuring Gemini API...")
            genai.configure(api_key=self._api_key)
            
            # Initialize model with minimal config
            logger.info("Creating Gemini model...")
            self.model = genai.GenerativeModel('gemini-pro')
            logger.info("Successfully initialized Gemini brain")
            
        except Exception as e:
            logger.error(f"Error initializing Gemini brain: {str(e)}")
            raise

    async def think(self, message: str, context: Dict, history: List[Dict]) -> str:
        """Process a message with context and history to generate a response."""
        try:
            # Create chat with optimized settings for speed
            model = genai.GenerativeModel(
                model_name='gemini-pro',
                generation_config={
                    'temperature': 0.7,  # Lower temperature for faster responses
                    'top_p': 0.1,  # Lower top_p for faster responses
                    'top_k': 1,  # Lower top_k for faster responses
                    'max_output_tokens': 1024,  # Reduced max tokens for speed
                },
                safety_settings=[
                    {
                        "category": "HARM_CATEGORY_HARASSMENT",
                        "threshold": "BLOCK_ONLY_HIGH"
                    },
                    {
                        "category": "HARM_CATEGORY_HATE_SPEECH",
                        "threshold": "BLOCK_ONLY_HIGH"
                    },
                    {
                        "category": "HARM_CATEGORY_SEXUALLY_EXPLICIT",
                        "threshold": "BLOCK_ONLY_HIGH"
                    },
                    {
                        "category": "HARM_CATEGORY_DANGEROUS_CONTENT",
                        "threshold": "BLOCK_ONLY_HIGH"
                    }
                ]
            )
            
            chat = model.start_chat(history=[])
            
            # Prepare a more specific prompt for faster responses
            prompt = f"""You are Octavia, a friendly and helpful AI assistant. Respond briefly and directly to: {message}"""
            
            # Send message with optimized settings
            response = await chat.send_message_async(
                prompt,
                generation_config=genai.types.GenerationConfig(
                    temperature=0.7,
                    candidate_count=1,
                    max_output_tokens=1024,
                    top_p=0.1,
                    top_k=1,
                )
            )
            
            if not response.text:
                return "I apologize, but I wasn't able to generate a proper response. Could you please try rephrasing your message?"
                
            return response.text.strip()
            
        except Exception as e:
            error_msg = f"I apologize, but I encountered an error: {str(e)}"
            print(f"Error in think: {error_msg}")
            return error_msg

    async def process_message(self, message: str) -> str:
        """Process a message and return the response"""
        try:
            return await self.think(message, {}, [])
        except Exception as e:
            return f"I apologize, but something went wrong: {str(e)}"

    async def test_api_key(self) -> bool:
        """Test if the API key is valid by making a minimal API call"""
        try:
            # Create a minimal test model
            test_model = genai.GenerativeModel('gemini-pro')
            
            # Make a minimal API call
            logger.debug("Testing API key with minimal request...")
            response = test_model.generate_content(
                "hello",
                generation_config={
                    'temperature': 0,
                    'candidate_count': 1,
                    'max_output_tokens': 1
                }
            )
            
            # Verify response
            if response and hasattr(response, 'text'):
                logger.info("API key validation successful")
                return True
                
            logger.error("Invalid API response")
            return False
            
        except Exception as e:
            error_msg = str(e).lower()
            logger.error(f"API key validation failed: {str(e)}")
            
            if "api_key_invalid" in error_msg:
                logger.error("Invalid API key format")
            elif "quota" in error_msg:
                logger.error("API quota exceeded")
                
            return False

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
