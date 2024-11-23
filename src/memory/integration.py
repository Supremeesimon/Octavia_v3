"""
Integrates memory system with Octavia's main functionality.
"""

from typing import Dict, Optional, Tuple
from .context.conversation import ConversationManager
from .patterns.command_learner import CommandPatternLearner

class MemoryIntegration:
    def __init__(self):
        self.conversation = ConversationManager()
        self.command_learner = CommandPatternLearner()

    def before_response(self, user_message: str) -> Dict:
        """Prepare context before responding to user."""
        # Get recent conversation context
        context = {
            "recent_conversations": self.conversation.get_recent_context(),
            "current_context": self.conversation.get_conversation_context()
        }
        
        return context

    def after_response(self, user_message: str, octavia_response: str, 
                      executed_command: Optional[str] = None,
                      command_success: bool = True,
                      command_intent: Optional[str] = None,
                      additional_context: Optional[Dict] = None):
        """Update memory after response."""
        # Save conversation
        self.conversation.add_exchange(
            user_message=user_message,
            octavia_response=octavia_response,
            additional_context=additional_context
        )

        # Learn from command if executed
        if executed_command and command_intent:
            self.command_learner.learn_from_success(
                command=executed_command,
                shell_type="powershell",  # or "cmd" based on actual usage
                intent=command_intent,
                success=command_success,
                context=additional_context
            )

    def suggest_command(self, intent: str, context: Optional[Dict] = None) -> Optional[str]:
        """Get command suggestion based on intent."""
        return self.command_learner.suggest_command(intent, context)

    def start_new_conversation(self):
        """Start a new conversation session."""
        self.conversation.start_new_conversation()

# Usage Example:
"""
memory = MemoryIntegration()

# Before processing user message
context = memory.before_response(user_message)

# After processing and executing command
memory.after_response(
    user_message="organize my downloads",
    octavia_response="I'll help organize your downloads folder",
    executed_command="Get-ChildItem Downloads | Sort-Object Extension",
    command_success=True,
    command_intent="organize_files",
    additional_context={"target_folder": "Downloads"}
)

# Get command suggestion
suggested_cmd = memory.suggest_command(
    intent="organize_files",
    context={"target_folder": "Downloads"}
)
"""
