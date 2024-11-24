"""
Filesystem Navigator for Octavia - Handles directory navigation and file management
"""

import os
import shutil
import subprocess
from pathlib import Path
from typing import List, Dict, Union, Tuple
from loguru import logger

class FilesystemNavigator:
    """Handles filesystem navigation and management with both cmd and powershell support"""
    
    def __init__(self):
        """Initialize the navigator with current location"""
        self.current_location = os.getcwd()
        self.previous_location = None
        self.command_shell = "cmd"  # Start with cmd, switch to powershell if needed
    
    def get_current_location(self) -> str:
        """Get current directory location"""
        return self.current_location
    
    def take_flight(self) -> Dict[str, Union[str, List[str]]]:
        """Get an overview of the filesystem from current location"""
        try:
            current = Path(self.current_location)
            parent_dirs = list(current.parents)
            sibling_dirs = [d for d in current.parent.iterdir() if d.is_dir()] if current.parent else []
            child_dirs = [d for d in current.iterdir() if d.is_dir()]
            
            return {
                "current": str(current),
                "parents": [str(p) for p in parent_dirs],
                "siblings": [str(s) for s in sibling_dirs],
                "children": [str(c) for c in child_dirs]
            }
        except Exception as e:
            logger.error(f"Error taking flight overview: {str(e)}")
            return {"error": str(e)}
    
    def survey_current_directory(self) -> Dict[str, List[str]]:
        """Get contents of current directory"""
        try:
            path = Path(self.current_location)
            files = [f for f in path.iterdir() if f.is_file()]
            directories = [d for d in path.iterdir() if d.is_dir()]
            
            return {
                "files": [str(f) for f in files],
                "directories": [str(d) for d in directories]
            }
        except Exception as e:
            logger.error(f"Error surveying directory: {str(e)}")
            return {"error": str(e)}
    
    def navigate_to(self, destination: str) -> Tuple[bool, str]:
        """Navigate to specified directory"""
        try:
            # Store current location before moving
            self.previous_location = self.current_location
            
            # Handle relative or absolute paths
            target = Path(destination).expanduser()
            if not target.is_absolute():
                target = Path(self.current_location) / target
            
            # Verify destination exists
            if not target.exists() or not target.is_dir():
                return False, f"Cannot find directory: {destination}"
            
            # Change directory
            os.chdir(str(target))
            self.current_location = str(target)
            return True, f"Successfully navigated to {destination}"
            
        except Exception as e:
            logger.error(f"Navigation error: {str(e)}")
            return False, str(e)
    
    def go_back(self) -> Tuple[bool, str]:
        """Return to previous directory"""
        if self.previous_location:
            result = self.navigate_to(self.previous_location)
            self.previous_location = None
            return result
        return False, "No previous location stored"
    
    def execute_command(self, command: str, use_powershell: bool = False) -> Tuple[bool, str]:
        """Execute a shell command, switching between cmd and powershell as needed"""
        try:
            shell = "powershell" if use_powershell else "cmd"
            if use_powershell:
                process = subprocess.Popen(
                    ["powershell", "-Command", command],
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    text=True
                )
            else:
                process = subprocess.Popen(
                    ["cmd", "/c", command],
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    text=True
                )
            
            stdout, stderr = process.communicate()
            
            if process.returncode == 0:
                return True, stdout
            else:
                # If cmd fails, try powershell and vice versa
                if not use_powershell:
                    logger.info("Command failed in cmd, trying powershell...")
                    return self.execute_command(command, use_powershell=True)
                return False, f"Error ({shell}): {stderr}"
                
        except Exception as e:
            logger.error(f"Command execution error: {str(e)}")
            return False, str(e)
    
    def organize_files(self, pattern: str = None, target_dir: str = None) -> Tuple[bool, str]:
        """Organize files in current directory based on pattern"""
        try:
            if not target_dir:
                target_dir = self.current_location
                
            path = Path(self.current_location)
            files = path.glob(pattern if pattern else "*")
            
            moved = 0
            for file in files:
                if file.is_file():
                    # Create target directory if it doesn't exist
                    Path(target_dir).mkdir(parents=True, exist_ok=True)
                    
                    # Move file to target directory
                    shutil.move(str(file), str(Path(target_dir) / file.name))
                    moved += 1
            
            return True, f"Successfully moved {moved} files to {target_dir}"
            
        except Exception as e:
            logger.error(f"File organization error: {str(e)}")
            return False, str(e)
