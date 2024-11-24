"""
Model management functionality for Octavia's brain.
"""

import os
from typing import Optional
import google.generativeai as genai
from loguru import logger
from dotenv import load_dotenv
import asyncio

class ModelManager:
    """Manages the Gemini model configuration and initialization"""
    
    def __init__(self, api_key: Optional[str] = None):
        """Initialize the model manager"""
        self.model = None
        self._api_key = None
        self._stop_requested = False
        if api_key:
            self._initialize_model(api_key)
    
    def _initialize_model(self, api_key: Optional[str] = None):
        """Initialize the Gemini model with configuration"""
        try:
            if not api_key:
                logger.error("No API key provided!")
                return
            
            # Clean and store the key
            self._api_key = api_key.strip()
            
            # Configure the client
            logger.info("Configuring Gemini API...")
            genai.configure(api_key=self._api_key)
            
            # Initialize model with Gemini 1.5 Flash config
            logger.info("Creating Gemini 1.5 Flash model for optimal performance...")
            self.model = genai.GenerativeModel(
                'gemini-1.5-flash',  # Using Flash for faster responses and better scaling
                generation_config={
                    'temperature': 0.7,
                    'top_p': 0.9,
                    'top_k': 20,
                    'max_output_tokens': 1024,  # Reduced for faster responses
                    'candidate_count': 1,  # Flash model optimization
                }
            )
            
            logger.info("Successfully initialized Gemini model")
            
        except Exception as e:
            logger.error(f"Error initializing model: {str(e)}")
            raise

    def request_stop(self):
        """Request to stop the current generation"""
        self._stop_requested = True

    def _reset_stop(self):
        """Reset the stop flag"""
        self._stop_requested = False

    async def test_connection(self) -> bool:
        """Test the API connection with a simple query"""
        try:
            logger.info("Testing API connection...")
            if not self.model:
                raise ValueError("Model not initialized. Please set API key first.")
                
            # Use the fastest possible validation
            response = await self.model.generate_content_async(
                "test",
                generation_config={
                    'temperature': 0,
                    'candidate_count': 1,
                    'max_output_tokens': 1,
                    'top_k': 1,
                    'top_p': 0
                },
                safety_settings=[]  # Skip safety checks for validation
            )
            
            # Quick validity check
            return bool(response and hasattr(response, 'text'))
                
        except Exception as e:
            logger.error(f"Error testing API connection: {str(e)}")
            return False

    async def generate_response(self, prompt: str) -> str:
        """Generate a response from the model"""
        try:
            if not self.model:
                raise ValueError("Model not initialized. Please set API key first.")
                
            self._reset_stop()
            
            # Create generation config for faster responses
            generation_config = {
                'temperature': 0.7,
                'top_p': 0.9,
                'top_k': 20,
                'max_output_tokens': 1024,
                'candidate_count': 1
            }
            
            # Use async generation with optimized config
            response = await asyncio.wait_for(
                self.model.generate_content_async(
                    prompt,
                    generation_config=generation_config
                ),
                timeout=30.0  # 30 second timeout for long responses
            )
            
            # Check for stop request immediately after generation
            if self._stop_requested:
                logger.info("Response generation stopped by user")
                return "[Response stopped by user]"
            
            if not response or not hasattr(response, 'text'):
                return "I'm drawing a blank at the moment. Could you rephrase that for me? 🤔"
            
            return response.text.strip()
            
        except asyncio.TimeoutError:
            logger.error("Response generation timed out")
            return "I apologize, but the response is taking too long. Please try a shorter query."
        except Exception as e:
            logger.error(f"Error generating response: {str(e)}")
            return f"I apologize, but something went wrong: {str(e)}"
