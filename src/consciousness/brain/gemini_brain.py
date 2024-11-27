"""
Gemini brain implementation for Octavia.
"""

import os
from typing import Dict, List, Optional, Union
from loguru import logger
import asyncio
import json
from datetime import datetime
import mimetypes
from .modules.model_manager import ModelManager
from .modules.conversation_manager import ConversationManager
from .modules.meta_reasoner import MetaReasoner

class GeminiBrain:
    """Brain implementation using Gemini 1.5 Flash"""
    
    # Maximum file size for different media types (in bytes)
    MAX_IMAGE_SIZE = 20 * 1024 * 1024  # 20MB
    MAX_VIDEO_SIZE = 100 * 1024 * 1024  # 100MB
    MAX_AUDIO_SIZE = 50 * 1024 * 1024   # 50MB
    
    def __init__(self, api_key: Optional[str] = None):
        """Initialize the brain with Gemini model"""
        self.model_manager = ModelManager(api_key)
        self.conversation_manager = ConversationManager(self)
        self.meta_reasoner = MetaReasoner()
        self._file_cache = {}
        self.interaction_context = {}
        self.is_processing = False
        self._chat = None
        self._stop_requested = False
        
        # Register abilities from model manager
        self.abilities = {}
        for ability_name, ability_data in self.model_manager.abilities.items():
            self.abilities[ability_name] = ability_data["enabled"]
            
        # Initialize chat if model is ready
        if self.model_manager.model:
            self._init_chat()
            
    def _init_chat(self):
        """Initialize chat session"""
        try:
            if not self.model_manager.model:
                logger.error("Model not initialized")
                return
            self._chat = self.model_manager.model.start_chat(history=[])
            logger.info("Chat session initialized")
        except Exception as e:
            logger.error(f"Failed to initialize chat: {e}")
            raise
            
    async def initialize(self):
        """Initialize the brain with API key"""
        try:
            await self.model_manager.initialize_model()
            logger.info("Brain initialized successfully")
            return True
        except Exception as e:
            logger.error(f"Failed to initialize brain: {e}")
            raise
            
    async def process_input(self, 
        message: str, 
        context: Optional[Dict] = None,
        media_files: Optional[List[Dict]] = None
    ) -> str:
        """Process input with support for multimodal content"""
        try:
            # Handle media files if present
            media_content = {}
            if media_files:
                media_tasks = []
                for file in media_files:
                    file_size = os.path.getsize(file['path'])
                    file_type = mimetypes.guess_type(file['path'])[0]
                    
                    # Check file size limits
                    if file_type.startswith('image/') and file_size > self.MAX_IMAGE_SIZE:
                        logger.warning(f"Image too large: {file_size} bytes")
                        continue
                    elif file_type.startswith('video/') and file_size > self.MAX_VIDEO_SIZE:
                        logger.warning(f"Video too large: {file_size} bytes")
                        continue
                    elif file_type.startswith('audio/') and file_size > self.MAX_AUDIO_SIZE:
                        logger.warning(f"Audio too large: {file_size} bytes")
                        continue
                    
                    cache_key = f"{file['path']}_{datetime.now().timestamp()}"
                    
                    if file_type.startswith('image/'):
                        task = asyncio.create_task(self._process_image(file, cache_key))
                        media_tasks.append(('images', task))
                    elif file_type.startswith('video/'):
                        task = asyncio.create_task(self._process_video(file, cache_key))
                        media_tasks.append(('video', task))
                    elif file_type.startswith('audio/'):
                        task = asyncio.create_task(self._process_audio(file, cache_key))
                        media_tasks.append(('audio', task))
                
                # Process all media files concurrently
                for media_type, task in media_tasks:
                    try:
                        result = await task
                        if media_type not in media_content:
                            media_content[media_type] = []
                        media_content[media_type].append(result)
                    except Exception as e:
                        logger.error(f"Error processing {media_type}: {str(e)}")
                        continue
                        
            # Get cached context if available
            cached_context = None
            if context and 'cache_key' in context:
                cached_context = self.model_manager.get_cached_context(context['cache_key'])
                
            # Prepare model inputs
            model_context = {
                'conversation_history': self.conversation_manager._conversation_history,  # Use full history
                'cached_context': cached_context,
                'media_content': media_content if media_content else None,
                'user_context': context if context else {}
            }
            
            # Generate response
            response = await self.generate_response(message)
            
            # Update conversation history
            self.conversation_manager.add_to_history(
                message, 
                response,
                media_content=media_content
            )
            
            return response
            
        except Exception as e:
            logger.error(f"Error processing input: {str(e)}")
            raise
            
    async def _process_image(self, file: Dict, cache_key: str) -> Dict:
        """Process and cache image file"""
        try:
            with open(file['path'], 'rb') as f:
                image_data = f.read()
            self._file_cache[cache_key] = {
                'data': image_data,
                'mime_type': mimetypes.guess_type(file['path'])[0]
            }
            return {'cache_key': cache_key}
        except Exception as e:
            logger.error(f"Error processing image: {str(e)}")
            raise
            
    async def _process_video(self, file: Dict, cache_key: str) -> Dict:
        """Process and cache video file"""
        try:
            # Use File API for video processing
            with open(file['path'], 'rb') as f:
                video_data = f.read()
            self._file_cache[cache_key] = {
                'data': video_data,
                'mime_type': mimetypes.guess_type(file['path'])[0]
            }
            return {'cache_key': cache_key}
        except Exception as e:
            logger.error(f"Error processing video: {str(e)}")
            raise
            
    async def _process_audio(self, file: Dict, cache_key: str) -> Dict:
        """Process and cache audio file"""
        try:
            with open(file['path'], 'rb') as f:
                audio_data = f.read()
            self._file_cache[cache_key] = {
                'data': audio_data,
                'mime_type': mimetypes.guess_type(file['path'])[0]
            }
            return {'cache_key': cache_key}
        except Exception as e:
            logger.error(f"Error processing audio: {str(e)}")
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

    async def validate_api_key(self, api_key: str) -> bool:
        """Validate the API key"""
        try:
            # Set the API key in model manager
            self.model_manager.api_key = api_key
            await self.model_manager.initialize_model()
            return await self.model_manager.validate_api_key(api_key)
        except Exception as e:
            logger.error(f"Error validating API key: {e}")
            return False

    def _enrich_context(self, context: Dict) -> Dict:
        """Enrich context with additional information"""
        if not context:
            context = {}
            
        enriched = {
            'system': self.model_manager.get_prompt(context),
            'user_context': {},
            'assistant_context': {},
            'environment': {},
            'spatial_context': {}  # New spatial context
        }
        
        # Add user technical level and preferences
        if hasattr(self.conversation_manager, '_user_style'):
            enriched['user_context'].update({
                'technical_level': self.conversation_manager._user_style.get('technical', 0.5),
                'formality': self.conversation_manager._user_style.get('formality', 0.5),
                'directness': self.conversation_manager._user_style.get('directness', 0.5),
                'verbosity': self.conversation_manager._user_style.get('verbosity', 0.5)
            })
        
        # Add conversation history summary if available
        if hasattr(self.conversation_manager, '_conversation_history'):
            history = self.conversation_manager._conversation_history[-10:]  # Last 5 exchanges
            if history:
                enriched['assistant_context']['recent_history'] = history
        
        # Add environmental context
        enriched['environment'].update({
            'timestamp': datetime.now().isoformat(),
            'timezone': datetime.now().astimezone().tzname(),
            'platform': os.name,
            'python_version': os.sys.version
        })
        
        # Add spatial awareness context
        try:
            current_location = self.meta_reasoner.check_current_location()
            spatial_map = self.meta_reasoner.analyze_directory_structure(os.getcwd())
            enriched['spatial_context'] = {
                'current_location': current_location,
                'spatial_map': spatial_map,
                'related_files': self.meta_reasoner.get_related_files(current_location)
            }
        except Exception as e:
            logger.warning(f"Could not enrich spatial context: {e}")
        
        # Merge with provided context
        for key in enriched:
            if key in context:
                if isinstance(context[key], dict):
                    enriched[key].update(context[key])
                else:
                    enriched[key] = context[key]
        
        return enriched

    async def generate_response(self, message: str) -> str:
        """Generate a response to the given message"""
        self._stop_requested = False
        
        try:
            logger.debug("Starting response generation...")
            if not self._chat:
                logger.debug("No chat session found, initializing...")
                self._init_chat()
                
            if not self._chat:
                logger.error("No chat session available")
                return "I'm sorry, but I'm not properly initialized yet. Please try again in a moment."
            
            # Generate response with streaming
            logger.debug("Starting streaming response...")
            response_chunks = []
            async for chunk in self.generate_stream(message):
                if self._stop_requested:
                    logger.info("Response generation stopped by user")
                    break
                response_chunks.append(chunk)
            
            # Combine chunks into final response
            response = "".join(response_chunks)
            logger.debug(f"Response generation complete: {len(response)} chars")
            
            return response
            
        except Exception as e:
            logger.error(f"Error generating response: {str(e)}")
            return f"I apologize, but I encountered an error: {str(e)}"

    async def generate_stream(self, message: str):
        """Generate a streaming response"""
        self._stop_requested = False
        
        try:
            logger.debug("Starting streaming response generation...")
            if not self._chat:
                logger.debug("No chat session found, initializing...")
                self._init_chat()
                
            if not self._chat:
                logger.error("No chat session available")
                yield "I'm sorry, but I'm not properly initialized yet. Please try again in a moment."
                return
                
            # Generate streaming response
            async for chunk in self.model_manager.generate_stream(message):
                if self._stop_requested:
                    logger.info("Response generation stopped by user")
                    break
                yield chunk
                await asyncio.sleep(0)  # Allow other tasks to run
                
        except Exception as e:
            logger.error(f"Error generating response: {str(e)}")
            yield f"I apologize, but I encountered an error: {str(e)}"

    async def think(self, message: str, context: Dict, history: List[Dict]) -> str:
        """Process a message with context and history to generate a response"""
        try:
            # For simple messages, use basic prompt
            if len(message.split()) <= 3 and not any(char in message for char in "?!."):
                return await self.generate_response(message)
            
            # For complex messages, use full context and available functions
            context['conversation_history'] = history
            functions = self.conversation_manager.get_available_functions()
            
            return await self.generate_response(message)
            
        except Exception as e:
            logger.error(f"Error in thinking process: {str(e)}")
            raise

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
        self.model_manager.clear_cache()

    def request_stop(self):
        """Request to stop the current response generation"""
        logger.info("Stop requested")
        self._stop_requested = True
        if self._chat:
            try:
                self._init_chat()  # Reset chat session
            except:
                pass
        
    async def update_interaction_context(self, context: dict):
        """Update brain's understanding of UI interaction context"""
        try:
            self.interaction_context.update(context)
            
            # If we have suggestions and aren't currently processing
            if (not self.is_processing and 
                context.get('suggestions') and 
                context['ui_interaction']['event_type'] != 'mouse_move'):
                
                # Consider making a contextual suggestion
                await self._consider_contextual_response(context)
                
        except Exception as e:
            logger.error(f"Error updating interaction context: {e}")
            
    async def _consider_contextual_response(self, context: dict):
        """Consider whether to make a contextual suggestion"""
        try:
            # Don't interrupt if already processing
            if self.is_processing:
                return
                
            suggestion = context['suggestions'][0]  # Get most relevant suggestion
            event = context['ui_interaction']
            
            # Check if suggestion is relevant enough
            if (event['event_type'] == 'hover' and event.get('hover_duration', 0) > 2.0) or \
               (event['event_type'] == 'click' and suggestion):
                
                # Generate subtle contextual response
                response = await self.generate_response(
                    "_ui_context_",  # Special trigger for UI context
                    additional_context={
                        "ui_event": event,
                        "suggestion": suggestion
                    }
                )
                
                if response:
                    # UI will handle showing this appropriately
                    pass
                    
        except Exception as e:
            logger.error(f"Error considering contextual response: {e}")
