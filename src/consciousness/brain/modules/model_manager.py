"""
Model management functionality for Octavia's brain.
"""

import os
from typing import Optional, Dict, List, Union
import google.generativeai as genai
from loguru import logger
from dotenv import load_dotenv
import asyncio
from google.generativeai.types import HarmCategory, HarmBlockThreshold
from datetime import datetime, timedelta

class ModelManager:
    """Manages the Gemini model configuration and initialization"""
    
    # Maximum cache size (100MB)
    MAX_CACHE_SIZE = 100 * 1024 * 1024
    
    def __init__(self, api_key: Optional[str] = None):
        """Initialize the model manager"""
        self.model = None
        self._api_key = None
        self._stop_requested = False
        self._context_cache = {}
        self._cache_size = 0
        if api_key:
            self._initialize_model(api_key)
    
    def _initialize_model(self, api_key: Optional[str] = None):
        """Initialize the Gemini model with configuration"""
        try:
            if not api_key:
                raise ValueError("API key is required")
            
            self._api_key = api_key.strip()
            
            # Configure the client
            logger.info("Configuring Gemini API...")
            genai.configure(api_key=self._api_key)
            
            # Initialize model with enhanced config
            logger.info("Creating Gemini model...")
            self.model = genai.GenerativeModel('gemini-1.5-flash',
                generation_config={
                    'temperature': 0.7,
                    'top_k': 20,
                    'top_p': 0.95,
                    'max_output_tokens': 2048,
                    'candidate_count': 1  # Optimize for single response
                },
                safety_settings={
                    HarmCategory.HARM_CATEGORY_HARASSMENT: HarmBlockThreshold.BLOCK_MEDIUM_AND_ABOVE,
                    HarmCategory.HARM_CATEGORY_HATE_SPEECH: HarmBlockThreshold.BLOCK_MEDIUM_AND_ABOVE,
                    HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT: HarmBlockThreshold.BLOCK_MEDIUM_AND_ABOVE,
                    HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT: HarmBlockThreshold.BLOCK_MEDIUM_AND_ABOVE,
                }
            )
            
            logger.info("Successfully initialized Gemini model")
            
        except Exception as e:
            logger.error(f"Error initializing model: {str(e)}")
            raise

    def _get_content_size(self, content: Union[str, Dict, List]) -> int:
        """Calculate approximate size of content in bytes"""
        if isinstance(content, str):
            return len(content.encode('utf-8'))
        return len(str(content).encode('utf-8'))

    def _cleanup_cache(self, required_size: int = 0):
        """Clean up cache to make space"""
        if self._cache_size <= self.MAX_CACHE_SIZE and required_size == 0:
            return

        # Sort by expiration time
        sorted_cache = sorted(
            self._context_cache.items(),
            key=lambda x: x[1]['expires']
        )

        # Remove entries until we have enough space
        for key, entry in sorted_cache:
            if self._cache_size + required_size <= self.MAX_CACHE_SIZE:
                break
            content_size = self._get_content_size(entry['chat'])
            self._cache_size -= content_size
            del self._context_cache[key]

    def cache_context(self, key: str, content: Union[str, Dict, List], ttl_hours: int = 24):
        """Cache context for reuse in future requests"""
        try:
            if not self.model:
                raise ValueError("Model not initialized")
            
            # Calculate content size
            content_size = self._get_content_size(content)
            
            # Clean up if needed
            self._cleanup_cache(content_size)
            
            # Check if content is too large
            if content_size > self.MAX_CACHE_SIZE:
                logger.warning(f"Content too large to cache: {content_size} bytes")
                return
            
            response = self.model.start_chat(context=content)
            self._context_cache[key] = {
                'chat': response,
                'expires': datetime.now() + timedelta(hours=ttl_hours)
            }
            self._cache_size += content_size
            logger.info(f"Cached context for key: {key} (size: {content_size} bytes)")
            
        except Exception as e:
            logger.error(f"Error caching context: {str(e)}")
            raise

    def get_cached_context(self, key: str) -> Optional[Dict]:
        """Retrieve cached context if available and not expired"""
        if key not in self._context_cache:
            return None
            
        cache_entry = self._context_cache[key]
        if datetime.now() > cache_entry['expires']:
            content_size = self._get_content_size(cache_entry['chat'])
            self._cache_size -= content_size
            del self._context_cache[key]
            return None
            
        return cache_entry['chat']

    def request_stop(self):
        """Request to stop the current generation"""
        self._stop_requested = True

    def _reset_stop(self):
        """Reset the stop flag"""
        self._stop_requested = False

    async def test_connection(self) -> bool:
        """Test the API connection with a simple query"""
        try:
            if not self.model:
                return False
                
            # Fastest possible validation
            response = await self.model.generate_content_async(
                "hi",
                generation_config={
                    'temperature': 0,
                    'max_output_tokens': 1,
                    'candidate_count': 1
                }
            )
            return bool(response and hasattr(response, 'text'))
                
        except Exception as e:
            logger.error(f"Error testing API connection: {str(e)}")
            return False

    async def generate_response(self, prompt: str, context: Dict = None, functions: List[Dict] = None) -> Union[str, Dict]:
        """Generate a response from the model with function calling support"""
        try:
            if not self.model:
                raise ValueError("Model not initialized")
                
            self._reset_stop()
            
            # Enhanced generation config
            generation_config = {
                'temperature': 0.7,
                'top_k': 20,  
                'max_output_tokens': 800,
                'candidate_count': 1,
                'top_p': 0.95,  # Nucleus sampling
            }
            
            # Build model request
            request = {
                'contents': self._build_contents(prompt, context),
                'generation_config': generation_config,
                'safety_settings': []
            }
            
            # Add function calling if provided
            if functions:
                request['tools'] = [{
                    'function_declarations': functions
                }]
            
            # Generate response
            response = await self.model.generate_content_async(**request)
            
            if self._stop_requested:
                return "[Response stopped by user]"
            
            # Handle function calling response
            if functions and response.candidates[0].content.parts[0].function_call:
                function_call = response.candidates[0].content.parts[0].function_call
                return {
                    'function_name': function_call.name,
                    'arguments': function_call.args
                }
                
            return response.text if response else ""
            
        except Exception as e:
            logger.error(f"Error generating response: {str(e)}")
            return f"Error: {str(e)}"

    def _build_contents(self, prompt: str, context: Dict = None) -> List[Dict]:
        """Build structured contents for the model request"""
        contents = []
        
        # Add context if provided
        if context:
            # System context
            if 'system' in context:
                contents.append({
                    'role': 'system',
                    'parts': [{'text': context['system']}]
                })
            
            # User context (e.g., preferences, history summaries)
            if 'user_context' in context:
                contents.append({
                    'role': 'user',
                    'parts': [{'text': f"Context: {context['user_context']}"}]
                })
            
            # Assistant context (e.g., previous decisions, reasoning)
            if 'assistant_context' in context:
                contents.append({
                    'role': 'assistant',
                    'parts': [{'text': f"Previous Context: {context['assistant_context']}"}]
                })
                
            # Environmental context (e.g., system state, time)
            if 'environment' in context:
                contents.append({
                    'role': 'system',
                    'parts': [{'text': f"Environment: {context['environment']}"}]
                })
        
        # Add the actual prompt
        contents.append({
            'role': 'user',
            'parts': [{'text': prompt}]
        })
        
        return contents
