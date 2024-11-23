"""
Handles chat interactions in Octavia's UI.
"""

from typing import Optional
from ..memory.ui_integration import UIMemoryBridge

class ChatHandler:
    def __init__(self):
        self.memory = UIMemoryBridge()

    async def handle_message(self, message: str):
        """Handle incoming user message."""
        try:
            # Get context from memory
            context = self.memory.pre_process_message(message)

            # Get AI response (your existing code)
            response = await self.get_ai_response(message, context)

            # Execute command if any
            command_result = await self.execute_command(response)

            # Update memory with results
            self.memory.post_process_response(
                message=message,
                response=response,
                command=command_result.command if command_result else None,
                success=command_result.success if command_result else True
            )

            return response

        except Exception as e:
            # Handle error and update memory
            self.memory.handle_command_execution(
                command="",
                success=False,
                intent="",
                error=str(e)
            )
            raise

    def start_new_chat(self):
        """Start a new chat session."""
        self.memory.start_new_session()

    async def get_ai_response(self, message: str, context: dict):
        """Get response from AI (your existing code)."""
        # Your existing AI response code here
        pass

    async def execute_command(self, response: str):
        """Execute command from response (your existing code)."""
        # Your existing command execution code here
        pass
