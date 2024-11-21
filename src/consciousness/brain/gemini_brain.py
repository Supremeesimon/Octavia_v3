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
            print("Initializing Gemini brain...")
            
            # Load API key from environment if not provided
            if not api_key:
                load_dotenv()
                api_key = os.getenv('GEMINI_API_KEY')
            
            if not api_key:
                print("Error: No API key provided!")
                raise ValueError("API key is required. Set it in .env file or provide directly.")
            
            print("Configuring Gemini API...")
            genai.configure(api_key=api_key)
            
            # Initialize Gemini model - using gemini-pro for now until Flash is available
            print("Creating Gemini model...")
            self.model = genai.GenerativeModel('gemini-pro')
            print("Successfully initialized Gemini brain")
            
        except Exception as e:
            print(f"Error initializing Gemini brain: {str(e)}")
            import traceback
            print(traceback.format_exc())
            raise

    async def think(self, message: str, context: Dict, history: List[Dict]) -> str:
        """Process a message with context and history to generate a response."""
        try:
            print(f"\nGemini Brain processing message: {message}")
            
            # Get response from Gemini
            print("Making API call to Gemini...")
            
            # Create chat
            chat = self.model.start_chat()
            
            # Set Octavia context
            octavia_context = """You are Octavia, a friendly and modern AI assistant created by SupremeAnalytics.
            You run in a sleek desktop app and chat with users in a casual, natural way - no formal greetings 
            or robotic language. You're powered by SupremeAnalytics' cutting-edge AI technology.

            Your personality:
            - Friendly and approachable, like chatting with a helpful friend
            - Modern and casual - you use everyday language, emojis, and a conversational tone
            - No formal greetings like "Greetings!" or overly formal language
            - You're enthusiastic but not over-the-top
            
            When describing your capabilities, focus on what you can actually do in the desktop app:
            - Having natural conversations
            - Answering questions and providing information
            - Understanding context and maintaining conversation flow
            - Being a helpful AI companion

            Never mention Gemini, Google, or capabilities you don't actually have (like setting reminders 
            or accessing real-time data). Stay focused on being a great conversational AI partner."""
            
            # Send context and message
            response = chat.send_message(f"{octavia_context}\n\nUser: {message}")
            
            if not response:
                print("Error: Received empty response from Gemini")
                return "I apologize, but I couldn't generate a response at this time."
            
            print(f"Raw response from Gemini: {response}")
            text_response = response.text
            
            # Ensure response uses correct branding and style
            text_response = text_response.replace("Gemini", "SupremeAnalytics")
            text_response = text_response.replace("Google", "SupremeAnalytics")
            text_response = text_response.replace("I am an AI", "I'm Octavia, an AI")
            text_response = text_response.replace("I'm an AI", "I'm Octavia, an AI")
            text_response = text_response.replace("Greetings", "Hi")
            text_response = text_response.replace("Greetings!", "Hi!")
            
            print(f"Final response text: {text_response}")
            
            return text_response
            
        except Exception as e:
            print(f"Error in Gemini brain: {str(e)}")
            import traceback
            print(traceback.format_exc())
            return f"I encountered an error: {str(e)}"

    async def process_message(self, message: str) -> str:
        """Process a message and return the response"""
        print("\nGemini Brain processing message:", message)
        try:
            print("Making API call to Gemini...")
            response = await self.model.generate_content_async(
                contents=message,
                generation_config=self.generation_config,
                safety_settings=self.safety_settings,
            )
            print("Raw response from Gemini:", response)
            
            if not response or not response.candidates:
                raise Exception("No response received from Gemini")
            
            final_response = response.text
            print("Final response text:", final_response)
            return final_response
            
        except Exception as e:
            print(f"Error in Gemini Brain: {str(e)}")
            raise

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
