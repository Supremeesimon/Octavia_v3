"""
Capability management for Octavia's prompt system
"""

from typing import Dict, List, Set
from loguru import logger
from google.generativeai.types import HarmCategory, HarmBlockThreshold

class CapabilityManager:
    """Manages prompt capabilities and safety settings"""
    
    # Safety settings
    SAFETY_SETTINGS = {
        HarmCategory.HARM_CATEGORY_HARASSMENT: HarmBlockThreshold.BLOCK_MEDIUM_AND_ABOVE,
        HarmCategory.HARM_CATEGORY_HATE_SPEECH: HarmBlockThreshold.BLOCK_MEDIUM_AND_ABOVE,
        HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT: HarmBlockThreshold.BLOCK_MEDIUM_AND_ABOVE,
        HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT: HarmBlockThreshold.BLOCK_MEDIUM_AND_ABOVE,
    }
    
    def __init__(self):
        """Initialize capability manager with core and extended capabilities"""
        self.core_capabilities = {
            'identity': {
                'priority': 0,
                'content': """Core Identity: Octavia v3 - Multimodal AI Assistant
Examples:
- Provide clear, contextual responses
- Adapt communication style to user
- Maintain consistent personality""",
            },
            'security': {
                'priority': 0,
                'content': """Security: Protection and Validation
Examples:
- Validate all operations
- Protect sensitive information
- Monitor security implications""",
            }
        }
        
        self.capability_modules = {
            'ui_awareness': {
                'priority': 1,
                'content': "UI Awareness: Monitor and respond to user interface interactions, window states, and visual elements."
            },
            'advanced_abilities': {
                'priority': 2,
                'content': "Advanced Abilities: Complex task handling, multi-step operations, and sophisticated problem-solving."
            },
            'performance': {
                'priority': 1,
                'content': "Performance Monitoring: Track system resources, optimize operations, and maintain efficiency."
            },
            'ml_capabilities': {
                'priority': 2,
                'content': "Machine Learning: Advanced pattern recognition, learning from interactions, and predictive capabilities."
            },
            'enhanced_security': {
                'priority': 1,
                'content': "Enhanced Security: Advanced threat detection, secure operations validation, and privacy protection."
            },
            'debugging': {
                'priority': 2,
                'content': "Advanced Debugging: Real-time monitoring, detailed interaction logging, performance metrics, and system state analysis."
            }
        }
        
        self._capability_usage: Dict[str, int] = {}
        
    def get_relevant_modules(self, context: Dict) -> Set[str]:
        """Get relevant capability modules based on context"""
        try:
            active_modules = set()
            
            # Core capabilities are always included
            active_modules.update(self.core_capabilities.keys())
            
            # Add context-specific capabilities
            if context.get('ui_interaction'):
                active_modules.add('ui_awareness')
                
            if context.get('security_sensitive'):
                active_modules.add('enhanced_security')
                
            if context.get('performance_critical'):
                active_modules.add('performance')
                
            if context.get('ml_required'):
                active_modules.add('ml_capabilities')
                
            if context.get('debugging_mode'):
                active_modules.add('debugging')
                
            if context.get('complex_task'):
                active_modules.add('advanced_abilities')
            
            # Update usage statistics
            for module in active_modules:
                self._capability_usage[module] = self._capability_usage.get(module, 0) + 1
            
            return active_modules
            
        except Exception as e:
            logger.error(f"Error getting relevant modules: {e}")
            return set(self.core_capabilities.keys())
    
    def get_capability_content(self, module_name: str) -> str:
        """Get content for a specific capability module"""
        try:
            if module_name in self.core_capabilities:
                return self.core_capabilities[module_name]['content']
            elif module_name in self.capability_modules:
                return self.capability_modules[module_name]['content']
            else:
                return ""
        except Exception as e:
            logger.error(f"Error getting capability content: {e}")
            return ""
    
    def get_usage_stats(self) -> Dict[str, int]:
        """Get capability usage statistics"""
        return dict(self._capability_usage)
    
    def apply_safety_filters(self, prompt: str) -> str:
        """Apply safety filters to prompt content"""
        try:
            safety_prefix = "Maintain appropriate, professional communication. "
            
            if 'system' in prompt.lower():
                safety_prefix += "Validate all system operations. "
            
            if 'user' in prompt.lower():
                safety_prefix += "Protect user privacy and data. "
            
            return safety_prefix + prompt
            
        except Exception as e:
            logger.error(f"Error applying safety filters: {e}")
            return prompt
