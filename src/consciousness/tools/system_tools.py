"""
System interaction tools for Octavia.
"""

import os
import sys
import psutil
import platform
from typing import Dict, List, Optional, Any
from loguru import logger
import subprocess
import asyncio

from .tool_system import tool, ToolCategory, ToolParameter

@tool(
    name="get_system_info",
    description="Get system information",
    category=ToolCategory.SYSTEM,
    parameters=[]
)
async def get_system_info() -> Dict[str, str]:
    """Get system information"""
    try:
        return {
            "os": platform.system(),
            "os_version": platform.version(),
            "architecture": platform.machine(),
            "processor": platform.processor(),
            "python_version": sys.version,
            "hostname": platform.node(),
            "cpu_count": os.cpu_count(),
            "memory_total": psutil.virtual_memory().total,
            "memory_available": psutil.virtual_memory().available,
            "disk_usage": str(psutil.disk_usage('/')),
        }
    except Exception as e:
        logger.error(f"Error getting system info: {str(e)}")
        raise

@tool(
    name="run_shell_command",
    description="Run a shell command",
    category=ToolCategory.SYSTEM,
    parameters=[
        ToolParameter("command", str, "Command to run", True),
        ToolParameter("cwd", str, "Working directory", True),
        ToolParameter("timeout", int, "Timeout in seconds", True)
    ]
)
async def run_shell_command(command: str, cwd: Optional[str] = None, timeout: Optional[int] = None) -> Dict[str, str]:
    """Run a shell command"""
    try:
        # Validate input
        if not command:
            raise ValueError("Command cannot be empty")
            
        # Set defaults
        if not cwd:
            cwd = os.getcwd()
        if not timeout:
            timeout = 30  # Default 30 second timeout
            
        # Run command
        logger.debug(f"Running command: {command} in {cwd}")
        process = await asyncio.create_subprocess_shell(
            command,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
            cwd=cwd
        )
        
        try:
            stdout, stderr = await asyncio.wait_for(
                process.communicate(),
                timeout=timeout
            )
            
            return {
                "stdout": stdout.decode() if stdout else "",
                "stderr": stderr.decode() if stderr else "",
                "returncode": process.returncode,
                "command": command,
                "cwd": cwd
            }
            
        except asyncio.TimeoutError:
            process.kill()
            raise TimeoutError(f"Command timed out after {timeout} seconds")
            
    except Exception as e:
        logger.error(f"Error running command: {str(e)}")
        raise

@tool(
    name="list_processes",
    description="List running processes",
    category=ToolCategory.SYSTEM,
    parameters=[
        ToolParameter("filter_name", str, "Filter processes by name", True)
    ]
)
async def list_processes(filter_name: Optional[str] = None) -> List[Dict[str, Any]]:
    """List running processes"""
    try:
        processes = []
        for proc in psutil.process_iter(['pid', 'name', 'cpu_percent', 'memory_percent']):
            try:
                pinfo = proc.info
                if not filter_name or filter_name.lower() in pinfo['name'].lower():
                    processes.append({
                        'pid': pinfo['pid'],
                        'name': pinfo['name'],
                        'cpu_percent': pinfo['cpu_percent'],
                        'memory_percent': pinfo['memory_percent']
                    })
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                pass
        return processes
    except Exception as e:
        logger.error(f"Error listing processes: {str(e)}")
        raise

@tool(
    name="get_environment_variables",
    description="Get environment variables",
    category=ToolCategory.SYSTEM,
    parameters=[
        ToolParameter("filter_key", str, "Filter variables by key", True)
    ]
)
async def get_environment_variables(filter_key: Optional[str] = None) -> Dict[str, str]:
    """Get environment variables"""
    try:
        env_vars = {}
        for key, value in os.environ.items():
            if not filter_key or filter_key.upper() in key.upper():
                env_vars[key] = value
        return env_vars
    except Exception as e:
        logger.error(f"Error getting environment variables: {str(e)}")
        raise
