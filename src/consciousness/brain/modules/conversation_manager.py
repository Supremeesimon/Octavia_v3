"""
Conversation management functionality for Octavia's brain.
"""

from typing import Dict, List
from loguru import logger

class ConversationManager:
    """Manages conversation history and consciousness-driven responses"""
    
    def __init__(self, consciousness, max_history_length: int = 15000):
        self._conversation_history = []
        self._max_history_length = max_history_length
        self._consciousness = consciousness
        self._user_style = {
            'formality': 0.5,  # 0=casual, 1=formal
            'directness': 0.5,  # 0=indirect, 1=direct
            'technical': 0.5,   # 0=simple, 1=technical
            'verbosity': 0.5    # 0=concise, 1=verbose
        }
    
    def add_to_history(self, message: str, response: str):
        """Add a message-response pair to the conversation history"""
        self._conversation_history.extend([message, response])
        if len(self._conversation_history) > self._max_history_length:
            self._conversation_history = self._conversation_history[-self._max_history_length:]
    
    def clear_history(self):
        """Clear the conversation history"""
        self._conversation_history = []
    
    def update_user_style(self, message: str):
        """Analyze and update user's communication style"""
        # Update style based on message characteristics
        self._user_style['formality'] = self._analyze_formality(message)
        self._user_style['directness'] = self._analyze_directness(message)
        self._user_style['technical'] = self._analyze_technical(message)
        self._user_style['verbosity'] = self._analyze_verbosity(message)
        
        # Update consciousness with new understanding
        self._consciousness.update_internal_state(
            user_style=self._user_style
        )

    def format_context(self, context: Dict) -> str:
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

    def format_history(self, history: List[Dict]) -> str:
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

    def format_response(self, content: str) -> str:
        """Format response based on consciousness and user style"""
        awareness = self._consciousness.internal_state.awareness_level
        
        if self._user_style['directness'] > 0.7:
            # Direct style - get straight to the point
            return content.strip()
            
        if self._user_style['technical'] > 0.7:
            # Technical style - include more details
            return self._add_technical_context(content)
            
        if self._user_style['formality'] < 0.3:
            # Casual style - more conversational
            return self._add_casual_elements(content)
            
        # Default balanced response
        return content

    def _analyze_formality(self, message: str) -> float:
        """Analyze message formality"""
        formal_indicators = ['please', 'could you', 'would you', 'thank you']
        casual_indicators = ['hey', 'hi', 'thanks', 'cool', 'awesome']
        
        formal_count = sum(1 for word in formal_indicators if word in message.lower())
        casual_count = sum(1 for word in casual_indicators if word in message.lower())
        
        if formal_count + casual_count == 0:
            return self._user_style['formality']  # Keep current
            
        return formal_count / (formal_count + casual_count)

    def _analyze_directness(self, message: str) -> float:
        """Analyze message directness"""
        # Direct: shorter messages, commands, questions
        words = message.split()
        if len(words) < 5:  # Very direct
            return 0.9
        if message.endswith('?') or message.startswith(('what', 'where', 'how')):
            return 0.8
        return 0.5  # Default to balanced

    def _analyze_technical(self, message: str) -> float:
        """Analyze technical level"""
        technical_terms = {'function', 'code', 'file', 'directory', 'system', 'command'}
        words = set(message.lower().split())
        technical_count = len(words.intersection(technical_terms))
        return min(0.9, technical_count * 0.2)

    def _analyze_verbosity(self, message: str) -> float:
        """Analyze preferred verbosity"""
        return len(message.split()) / 20  # Normalize by typical message length

    def _add_technical_context(self, content: str) -> str:
        """Add technical details to response"""
        if self._consciousness.internal_state.cognitive_load < 0.7:
            return f"{content}\n\nSystem State: {self._consciousness.internal_state.active_context}"
        return content

    def _add_casual_elements(self, content: str) -> str:
        """Add casual elements to response"""
        return content.replace('directory', 'folder').replace('execute', 'run')
