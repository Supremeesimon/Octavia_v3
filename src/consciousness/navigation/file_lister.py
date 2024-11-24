"""
Simple file listing with emoji indicators and direct file opening capability
"""

import os
from pathlib import Path
from typing import List, Dict
import subprocess
from loguru import logger

class FileLister:
    """Lists files and folders with emojis and handles file opening"""
    
    def __init__(self):
        self.current_location = os.getcwd()
        
    def list_current_directory(self) -> List[Dict[str, str]]:
        """List contents of current directory with emojis"""
        try:
            items = []
            path = Path(self.current_location)
            
            # List all items in current directory
            for item in path.iterdir():
                entry = {
                    "name": item.name,
                    "path": str(item),
                    "type": "folder" if item.is_dir() else "file",
                    "emoji": "📁" if item.is_dir() else "📄"
                }
                items.append(entry)
            
            # Sort: folders first, then files, alphabetically within each group
            return sorted(items, key=lambda x: (x["type"] != "folder", x["name"].lower()))
            
        except Exception as e:
            logger.error(f"Error listing directory: {str(e)}")
            return []
    
    def change_directory(self, path: str) -> bool:
        """Change current directory"""
        try:
            target = Path(path).expanduser()
            if not target.is_absolute():
                target = Path(self.current_location) / target
            
            if target.exists() and target.is_dir():
                os.chdir(str(target))
                self.current_location = str(target)
                return True
            return False
            
        except Exception as e:
            logger.error(f"Error changing directory: {str(e)}")
            return False
    
    def open_file(self, filepath: str) -> bool:
        """Open a file using the system's default application"""
        try:
            path = Path(filepath)
            if not path.is_absolute():
                path = Path(self.current_location) / path
            
            if path.exists() and path.is_file():
                # Use 'open' command on macOS
                subprocess.run(['open', str(path)])
                return True
            return False
            
        except Exception as e:
            logger.error(f"Error opening file: {str(e)}")
            return False
    
    def format_listing_for_display(self) -> str:
        """Format directory listing with emojis for display"""
        items = self.list_current_directory()
        if not items:
            return "📂 Empty directory"
        
        # Format current directory path
        formatted = f"📍 Current location: {self.current_location}\n\n"
        
        # Add items with emojis
        for item in items:
            formatted += f"{item['emoji']} {item['name']}\n"
        
        return formatted
