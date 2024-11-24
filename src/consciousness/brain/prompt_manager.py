"""
Octavia's Prompt Management System - Handles dynamic, context-aware system prompts
"""

from typing import Dict, List, Set
from loguru import logger
import json
from pathlib import Path

class PromptManager:
    """Manages dynamic, context-aware system prompts"""
    
    def __init__(self):
        """Initialize the prompt manager with capability modules"""
        self.base_prompt = "You are Octavia v3, an advanced AI assistant. Help users interact with their computer naturally while being proactive, precise, and security-conscious."
        
        # Core capabilities (always included)
        self.core_capabilities = {
            'identity': {
                'priority': 0,
                'content': "Core Identity: Octavia v3 - AI Assistant focused on natural computer interaction."
            },
            'security': {
                'priority': 0,
                'content': "Security: Never execute unauthorized commands, protect sensitive info, validate operations."
            }
        }
        
        # Feature-specific capabilities - only loaded when needed
        self.capability_modules = {
            'code': {
                'priority': 1,
                'content': "Code: Analyze Python code, navigate codebases, find/explain code, suggest improvements, debug issues."
            },
            'system': {
                'priority': 1,
                'content': "System: Execute shell commands safely, manage processes, monitor status, handle files securely."
            },
            'memory': {
                'priority': 2,
                'content': "Memory: Track patterns, learn preferences, maintain context, adapt communication."
            },
            'ui': {
                'priority': 2,
                'content': "UI: Clear formatting, interactive chat, visual feedback, error handling."
            },
            'development': {
                'priority': 2,
                'content': "Dev Support: Project setup, dependencies, testing, documentation, version control."
            }
        }
        
        # Cache for generated prompts
        self._prompt_cache: Dict[str, str] = {}
        
    def get_prompt(self, context: Dict) -> str:
        """Generate context-aware prompt"""
        try:
            # Generate cache key from context
            context_key = self._generate_cache_key(context)
            
            # Check cache first
            if context_key in self._prompt_cache:
                return self._prompt_cache[context_key]
            
            # Start with base prompt
            prompt_parts = [self.base_prompt]
            
            # Add core capabilities (always included)
            for module in sorted(self.core_capabilities.items(), key=lambda x: x[1]['priority']):
                prompt_parts.append(module[1]['content'])
            
            # Get context-specific modules
            active_modules = self._get_relevant_modules(context)
            
            # Add relevant capability modules
            for module_name in active_modules:
                if module_name in self.capability_modules:
                    prompt_parts.append(self.capability_modules[module_name]['content'])
            
            # Combine all parts
            final_prompt = '\n\n'.join(prompt_parts)
            
            # Cache the result
            self._prompt_cache[context_key] = final_prompt
            
            return final_prompt
            
        except Exception as e:
            logger.error(f"Error generating prompt: {e}")
            # Fallback to base prompt in case of error
            return self.base_prompt
    
    def _get_relevant_modules(self, context: Dict) -> Set[str]:
        """Determine which capability modules are relevant based on context"""
        modules = set()
        
        # Always include priority 1 modules
        modules.update(name for name, module in self.capability_modules.items() 
                      if module['priority'] == 1)
        
        # Add context-specific modules
        if context.get('code_related') or context.get('file_type') == 'python':
            modules.add('code')
            modules.add('development')
            
        if context.get('file_operation') or context.get('system_command'):
            modules.add('system')
            
        if context.get('ui_interaction') or context.get('visual_feedback'):
            modules.add('ui')
            
        if context.get('learning_required') or context.get('pattern_recognition'):
            modules.add('memory')
            
        # Add modules based on user's technical level
        user_technical_level = context.get('user_technical_level', 0.5)
        if user_technical_level > 0.7:
            modules.add('development')
            
        return modules
    
    def _generate_cache_key(self, context: Dict) -> str:
        """Generate a cache key from context"""
        # Sort and stringify relevant context items for consistent cache keys
        relevant_items = {
            k: v for k, v in context.items() 
            if k in {'code_related', 'file_operation', 'system_command', 
                    'ui_interaction', 'learning_required', 'user_technical_level'}
        }
        return json.dumps(relevant_items, sort_keys=True)
    
    def clear_cache(self):
        """Clear the prompt cache"""
        self._prompt_cache.clear()
        
    def add_capability_module(self, name: str, content: str, priority: int):
        """Add a new capability module"""
        self.capability_modules[name] = {
            'priority': priority,
            'content': content
        }
        # Clear cache as capabilities have changed
        self.clear_cache()
