"""
Handles chat interactions in Octavia's UI.
"""

from typing import Optional, Dict, List
from dataclasses import dataclass
import os
import mimetypes
from ..memory.ui_integration import UIMemoryBridge
from ..consciousness.tools.system_tools import run_shell_command

@dataclass
class CommandResult:
    command: str
    success: bool
    output: Optional[str] = None
    error: Optional[str] = None

@dataclass
class UploadedFile:
    path: str
    mime_type: str
    size: int
    name: str

class ChatHandler:
    def __init__(self):
        self.memory = UIMemoryBridge()
        self.upload_dir = os.path.join(os.path.expanduser("~"), ".octavia", "uploads")
        os.makedirs(self.upload_dir, exist_ok=True)

    async def handle_message(self, message: str, uploaded_files: Optional[List[UploadedFile]] = None):
        """Handle incoming user message with optional file uploads."""
        try:
            # Process uploaded files
            media_files = []
            if uploaded_files:
                for file in uploaded_files:
                    media_files.append({
                        'path': file.path,
                        'mime_type': file.mime_type,
                        'name': file.name
                    })

            # Get context from memory
            context = self.memory.pre_process_message(message)
            
            # Add file context
            if media_files:
                context['media_files'] = media_files

            # Get AI response with media context
            response = await self.get_ai_response(message, context)

            # Execute command if any
            command_result = await self.execute_command(response)

            # Update memory with results
            self.memory.post_process_response(
                message=message,
                response=response,
                command=command_result.command if command_result else None,
                success=command_result.success if command_result else True,
                media_files=media_files
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

    async def handle_file_upload(self, file_data: bytes, filename: str) -> UploadedFile:
        """Handle file upload from UI."""
        try:
            # Generate safe filename
            safe_filename = os.path.join(self.upload_dir, filename)
            
            # Save file
            with open(safe_filename, 'wb') as f:
                f.write(file_data)
                
            # Get file info
            mime_type = mimetypes.guess_type(filename)[0] or 'application/octet-stream'
            size = os.path.getsize(safe_filename)
            
            return UploadedFile(
                path=safe_filename,
                mime_type=mime_type,
                size=size,
                name=filename
            )
            
        except Exception as e:
            raise Exception(f"Failed to handle file upload: {str(e)}")

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
