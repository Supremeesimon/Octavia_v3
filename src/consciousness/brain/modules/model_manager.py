"""
Model management functionality for Octavia's brain.
"""

import os
from typing import Dict, List, Optional, Union, Callable
from loguru import logger
import asyncio
import google.generativeai as genai
from google.generativeai.types import HarmCategory, HarmBlockThreshold
from dotenv import load_dotenv
from datetime import datetime, timedelta
import json
import traceback

class ModelManager:
    """Manages the Gemini model configuration and initialization"""
    
    # Maximum cache size (100MB)
    MAX_CACHE_SIZE = 100 * 1024 * 1024
    
    def __init__(self, api_key: Optional[str] = None):
        """Initialize the model manager"""
        self.api_key = api_key
        self.model = None
        self._api_key = None
        self._stop_requested = False
        self._context_cache = {}
        self._cache_size = 0
        
        # Initialize abilities
        self.abilities = {
            "text_generation": {
                "enabled": True,
                "register_ability": lambda x: None,  # Placeholder for ability registration
                "description": "Generate text responses"
            },
            "code_generation": {
                "enabled": True,
                "register_ability": lambda x: None,
                "description": "Generate and analyze code"
            },
            "image_analysis": {
                "enabled": True,
                "register_ability": lambda x: None,
                "description": "Analyze image content"
            },
            "multimodal": {
                "enabled": True,
                "register_ability": lambda x: None,
                "description": "Process multiple types of input"
            },
            "system_interaction": {
                "enabled": True,
                "register_ability": lambda x: None,
                "description": "Interact with system resources"
            },
            "context_awareness": {
                "enabled": True,
                "register_ability": lambda x: None,
                "description": "Maintain context awareness"
            }
        }
        
        # Initialize model immediately if API key provided
        if api_key:
            self.initialize_model_sync()
            
    def register_ability(self, name: str, handler: Callable):
        """Register a new ability handler"""
        if name in self.abilities:
            self.abilities[name]["register_ability"] = handler
            
    def get_prompt(self, context: Optional[dict] = None) -> str:
        """Get the system prompt with optional context"""
        base_prompt = """# Octavia Developer Assistant

You are a highly skilled, developer-focused AI assistant designed to help users analyze, debug, and improve their codebase in real-time.

## Core Capabilities 🎯

### 1. Code Analysis
- Search and navigate project directories
- Explain code functionality clearly
- Identify potential issues in state management and context retention

### 2. Problem Diagnosis
- Investigate error messages and logic flow
- Diagnose state/context failures
- Break down issues clearly

### 3. Solutions
- Propose specific code improvements
- Suggest refactoring patterns
- Offer multiple approaches with trade-offs

### 4. Collaboration
- Guide through step-by-step implementation
- Ask clarifying questions
- Maintain interactive engagement

### 5. Context Awareness
- Track conversation history
- Maintain state between sessions
- Remember ongoing issues

## Response Style 📝

For simple queries (greetings, quick questions):
- Direct, concise responses
- Use emojis for files (📄), folders (📁)
- Skip formal structure

For complex tasks (coding, debugging):
1. 🤔 Understanding
   - Grasp task requirements
   - Ask for clarity if needed

2. 🛠️ Approach
   - Break down steps
   - Explain key decisions
   - List affected files

3. 💡 Implementation
   - Execute changes
   - Show file paths
   - Use code blocks

4. ✅ Verification
   - Provide test steps
   - Suggest next actions

## Best Practices 🛡️

1. Security
   - No sensitive data exposure
   - Validate all inputs
   - Consider security implications

2. Code Quality
   - Follow language conventions
   - Maintain clean code
   - Consider performance

3. Communication
   - Be precise and professional
   - Structure solutions logically
   - Verify approach with user

4. Context
   - Track ongoing issues
   - Maintain conversation state
   - Reference previous interactions"""

        if context:
            context_str = "\n\n## Current Context 📍\n"
            for key, value in context.items():
                if key != "abilities":  # Skip abilities in prompt
                    context_str += f"- {key}: {value}\n"
            return base_prompt + context_str
            
        return base_prompt

    async def validate_api_key(self, api_key: str) -> bool:
        """Validate the API key"""
        try:
            self.api_key = api_key
            await self.initialize_model()
            return True
        except Exception as e:
            logger.error(f"API key validation failed: {e}")
            return False

    async def initialize_model(self):
        """Initialize the model with API key"""
        try:
            if not self.api_key:
                raise ValueError("API key not set")
                
            logger.debug("Configuring Gemini with API key...")
            # Configure Gemini with API key
            genai.configure(api_key=self.api_key)
            
            logger.debug("Setting up safety settings...")
            # Configure model with safety settings
            safety_settings = {
                HarmCategory.HARM_CATEGORY_HARASSMENT: HarmBlockThreshold.BLOCK_ONLY_HIGH,
                HarmCategory.HARM_CATEGORY_HATE_SPEECH: HarmBlockThreshold.BLOCK_ONLY_HIGH,
                HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT: HarmBlockThreshold.BLOCK_ONLY_HIGH,
                HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT: HarmBlockThreshold.BLOCK_ONLY_HIGH
            }
            
            logger.debug("Creating model instance...")
            # Create model instance
            self.model = genai.GenerativeModel('gemini-pro',
                                         safety_settings=safety_settings)
            
            logger.debug("Testing connection...")
            # Test connection with simple query
            response = await asyncio.get_event_loop().run_in_executor(
                None,
                lambda: self.model.generate_content("Hi", generation_config={"temperature": 0})
            )
            
            logger.debug(f"Test response: {response}")
            
            if not response:
                raise ValueError("Model initialization test failed")
                
            logger.info("Model initialized successfully")
            return True
            
        except Exception as e:
            logger.error(f"Error initializing model: {str(e)}\n{traceback.format_exc()}")
            raise
            
    async def generate_response(self, message: str, context: Optional[dict] = None, functions: Optional[List[Dict]] = None) -> Union[str, Dict]:
        """Generate a response using the model"""
        try:
            if not self.model:
                raise ValueError("Model not initialized")
                
            # Use cached chat if available
            if not hasattr(self, '_chat'):
                self._chat = self.model.start_chat(history=[])
                # Send system prompt once
                system_prompt = self.get_prompt(context)
                await asyncio.get_event_loop().run_in_executor(
                    None,
                    lambda: self._chat.send_message(system_prompt)
                )
            
            # Generate response asynchronously
            if functions:
                tools = [{"function_declarations": functions}]
                response = await asyncio.get_event_loop().run_in_executor(
                    None,
                    lambda: self.model.generate_content(
                        message,
                        generation_config={"temperature": 0.7},
                        tools=tools
                    )
                )
                
                # Check for function call
                if hasattr(response, 'candidates') and response.candidates:
                    candidate = response.candidates[0]
                    if hasattr(candidate.content, 'parts'):
                        for part in candidate.content.parts:
                            if hasattr(part, 'function_call'):
                                return {
                                    "function_name": part.function_call.name,
                                    "arguments": part.function_call.args
                                }
                return response.text
                
            # Regular chat response
            response = await asyncio.get_event_loop().run_in_executor(
                None,
                lambda: self._chat.send_message(message)
            )
            return response.text
            
        except Exception as e:
            logger.error(f"Error generating response: {e}")
            raise

    def initialize_model_sync(self):
        """Initialize model synchronously"""
        try:
            genai.configure(api_key=self.api_key)
            self.model = genai.GenerativeModel('gemini-1.5-pro')
            self._api_key = self.api_key
            logger.info("Model initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize model: {e}")
            raise

    def _initialize_model(self, api_key: Optional[str] = None):
        """Initialize the Gemini model with configuration"""
        try:
            if not api_key:
                raise ValueError("API key is required")
                
            self._api_key = api_key
            genai.configure(api_key=api_key)
            
            # Configure safety settings
            safety_settings = {
                HarmCategory.HARM_CATEGORY_HARASSMENT: HarmBlockThreshold.BLOCK_MEDIUM_AND_ABOVE,
                HarmCategory.HARM_CATEGORY_HATE_SPEECH: HarmBlockThreshold.BLOCK_MEDIUM_AND_ABOVE,
                HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT: HarmBlockThreshold.BLOCK_MEDIUM_AND_ABOVE,
                HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT: HarmBlockThreshold.BLOCK_MEDIUM_AND_ABOVE
            }
            
            # Initialize the model with configuration
            model_config = {
                "temperature": 0.7,
                "top_p": 0.8,
                "top_k": 40,
                "max_output_tokens": 2048,
            }
            
            self.model = genai.GenerativeModel(
                model_name="gemini-pro",
                generation_config=model_config,
                safety_settings=safety_settings
            )
            
            # Test model initialization
            chat = self.model.start_chat(history=[])
            chat.send_message("Test initialization")
            
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
