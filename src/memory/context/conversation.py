"""
Manages conversation context and state for Octavia.
"""

import uuid
from typing import Optional, Dict, List
from ..database.manager import DatabaseManager

class ConversationManager:
    def __init__(self):
        self.db = DatabaseManager()
        self.current_conversation_id = str(uuid.uuid4())
        self.current_context = {}

    def start_new_conversation(self):
        """Start a new conversation with fresh context."""
        self.current_conversation_id = str(uuid.uuid4())
        self.current_context = {}

    def add_exchange(self, user_message: str, octavia_response: str, 
                    additional_context: Optional[Dict] = None):
        """Add a conversation exchange and update context."""
        # Update current context
        if additional_context:
            self.current_context.update(additional_context)

        # Save to database
        self.db.save_conversation(
            user_message=user_message,
            octavia_response=octavia_response,
            context_data=self.current_context,
            conversation_id=self.current_conversation_id
        )

    def get_conversation_context(self) -> Dict:
        """Get current conversation context."""
        return self.current_context

    def get_recent_context(self, message_limit: int = 5) -> List[Dict]:
        """Get recent conversation history with context."""
        return self.db.get_recent_conversations(limit=message_limit)

    def update_context(self, new_context: Dict):
        """Update the current conversation context."""
        self.current_context.update(new_context)
