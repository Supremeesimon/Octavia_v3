"""
Integrates memory system with Octavia's UI components.
"""

from typing import Optional, Dict, List
from .integration import MemoryIntegration

class UIMemoryBridge:
    def __init__(self):
        self.memory = MemoryIntegration()
        self._current_command: Optional[str] = None
        self._current_intent: Optional[str] = None
        self._current_media: Optional[List[Dict]] = None

    def pre_process_message(self, message: str) -> Dict:
        """Process message before sending to AI."""
        context = self.memory.before_response(message)
        
        # Add current media context if available
        if self._current_media:
            context['media_context'] = self._current_media
            
        return {
            "context": context,
            "suggested_command": None
        }

    def post_process_response(self, message: str, response: str, 
                            command: Optional[str] = None,
                            success: bool = True,
                            media_files: Optional[List[Dict]] = None):
        """Process AI response and update memory."""
        self._current_command = command
        self._current_media = media_files
        
        # Update memory with conversation, command results, and media
        self.memory.after_response(
            user_message=message,
            octavia_response=response,
            executed_command=command,
            command_success=success,
            command_intent=self._current_intent,
            additional_context={'media_files': media_files} if media_files else None
        )

    def handle_command_execution(self, command: str, success: bool, 
                               intent: str, error: Optional[str] = None):
        """Handle command execution results."""
        self._current_intent = intent
        context = {
            "error": error,
            "last_command": command,
            "media_files": self._current_media
        }
        
        self.memory.after_response(
            user_message="",  # Already saved in post_process_response
            octavia_response="",
            executed_command=command,
            command_success=success,
            command_intent=intent,
            additional_context=context
        )

    def get_command_suggestions(self, intent: str) -> Optional[str]:
        """Get command suggestions based on intent."""
        return self.memory.suggest_command(intent)

    def start_new_session(self):
        """Start a new chat session."""
        self.memory.start_new_conversation()
        self._current_command = None
        self._current_intent = None
        self._current_media = None
