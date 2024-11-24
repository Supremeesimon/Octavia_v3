"""
Command processing functionality for Octavia's brain.
"""

import os
from datetime import datetime
from typing import Dict, List
from loguru import logger

from ...tools.system_tools import run_shell_command
from ...tools.file_tools import list_directory

class CommandProcessor:
    """Handles consciousness-aware command processing"""
    
    def __init__(self, consciousness, conversation_manager):
        self._consciousness = consciousness
        self._conversation = conversation_manager
        
    async def process_command(self, command: str) -> str:
        """Process command through consciousness system"""
        # Update consciousness state
        self._consciousness.update_internal_state(
            current_goals=['process_command'],
            cognitive_load=0.3  # Command processing is a basic task
        )
        
        # Update user's communication style
        self._conversation.update_user_style(command)
        
        # Get command response
        response = await self._get_command_response(command)
        
        # Format through conversation manager
        return self._conversation.format_response(response)
        
    async def _get_command_response(self, command: str) -> str:
        """Get raw command response"""
        if 'directory' in command.lower() or 'folder' in command.lower():
            return await self._handle_directory_command(command)
        elif 'file' in command.lower():
            return await self._handle_file_command(command)
        else:
            return await self._handle_general_command(command)
            
    async def _handle_directory_command(self, command: str) -> str:
        """Handle directory-related commands"""
        try:
            current_dir = os.getcwd()
            
            if 'what' in command or 'current' in command:
                return current_dir
                
            if 'list' in command or 'show' in command:
                files = await list_directory(current_dir)
                if not files:
                    return "This directory is empty."
                    
                # Format based on user's technical level
                if self._conversation._user_style['technical'] > 0.7:
                    return self._format_technical_listing(files)
                else:
                    return self._format_simple_listing(files)
                    
        except Exception as e:
            logger.error(f"Directory command error: {e}")
            return f"I encountered an error: {str(e)}"
            
    def _format_technical_listing(self, files: List[str]) -> str:
        """Format listing for technical users"""
        formatted = []
        for file_path in files:
            stat = os.stat(file_path)
            size = self._format_size(stat.st_size)
            mtime = datetime.fromtimestamp(stat.st_mtime)
            formatted.append(f"{os.path.basename(file_path)} ({size}, {mtime})")
        return "\n".join(formatted)
        
    def _format_simple_listing(self, files: List[str]) -> str:
        """Format listing for non-technical users"""
        return "\n".join(os.path.basename(f) for f in files)
        
    def _format_size(self, size: int) -> str:
        """Format file size in human readable format"""
        for unit in ['B', 'KB', 'MB', 'GB']:
            if size < 1024:
                return f"{size:.1f}{unit}"
            size /= 1024
        return f"{size:.1f}TB"

    async def _handle_file_command(self, command: str) -> str:
        """Handle file-related commands"""
        try:
            # TO DO: implement file command handling
            return "File command handling not implemented yet."
        except Exception as e:
            logger.error(f"File command error: {e}")
            return f"I encountered an error: {str(e)}"

    async def _handle_general_command(self, command: str) -> str:
        """Handle general commands"""
        try:
            result = await run_shell_command(command)
            output = result.get("stdout", "").strip()
            error = result.get("stderr", "").strip()
            
            if result.get("returncode") == 0:
                return output
            else:
                return f"Hmm, that didn't work quite right. Here's what happened:\n{error}"
        except Exception as e:
            logger.error(f"Error executing command: {str(e)}")
            return f"I ran into a small hiccup with that command: {str(e)} 😅"
