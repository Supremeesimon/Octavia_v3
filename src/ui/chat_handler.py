"""
Handles chat interactions in Octavia's UI.
"""

from typing import Optional, Dict
from dataclasses import dataclass
from ..memory.ui_integration import UIMemoryBridge
from ..consciousness.tools.system_tools import run_shell_command

@dataclass
class CommandResult:
    command: str
    success: bool
    output: Optional[str] = None
    error: Optional[str] = None

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

            # Format response with command output if available
            if command_result and command_result.output:
                response = f"{response}\n\nCommand Output:\n```\n{command_result.output}\n```"
            elif command_result and command_result.error:
                response = f"{response}\n\nCommand Error:\n```\n{command_result.error}\n```"

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

    async def execute_command(self, response: str) -> Optional[CommandResult]:
        """Execute command from response."""
        try:
            # Extract command from response (implement command extraction logic)
            command = self._extract_command(response)
            if not command:
                return None

            # Execute command using system_tools
            result = await run_shell_command(command)

            return CommandResult(
                command=command,
                success=result["returncode"] == 0,
                output=result["stdout"] if result["returncode"] == 0 else None,
                error=result["stderr"] if result["returncode"] != 0 else None
            )

        except Exception as e:
            return CommandResult(
                command=command if 'command' in locals() else "",
                success=False,
                error=str(e)
            )

    def _extract_command(self, response: str) -> Optional[str]:
        """Extract command from AI response."""
        # Look for commands in markdown code blocks
        if "```" in response:
            blocks = response.split("```")
            for i in range(1, len(blocks), 2):
                if blocks[i].startswith("shell") or blocks[i].startswith("bash"):
                    return blocks[i].split("\n", 1)[1].strip()
                elif not any(blocks[i].startswith(lang) for lang in ["python", "javascript", "json"]):
                    return blocks[i].strip()
        return None
