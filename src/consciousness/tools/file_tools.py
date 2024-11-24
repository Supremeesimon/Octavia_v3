"""
File system tools for Octavia.
"""

import os
import shutil
from pathlib import Path
from typing import List, Optional, Dict, Any
from loguru import logger

from .tool_system import tool, ToolCategory, ToolParameter

@tool(
    name="list_directory",
    description="List contents of a directory",
    category=ToolCategory.FILE_SYSTEM,
    parameters=[
        ToolParameter("path", str, "Directory path to list", True),
        ToolParameter("recursive", bool, "List recursively", True)
    ]
)
async def list_directory(path: str, recursive: bool = False) -> Dict[str, Any]:
    """List contents of a directory"""
    try:
        path = Path(path)
        if not path.exists():
            raise FileNotFoundError(f"Directory not found: {path}")
        if not path.is_dir():
            raise NotADirectoryError(f"Not a directory: {path}")

        files = []
        if recursive:
            for p in path.rglob("*"):
                files.append({
                    "path": str(p),
                    "type": "directory" if p.is_dir() else "file",
                    "size": p.stat().st_size if p.is_file() else None,
                    "modified": p.stat().st_mtime
                })
        else:
            for p in path.iterdir():
                files.append({
                    "path": str(p),
                    "type": "directory" if p.is_dir() else "file",
                    "size": p.stat().st_size if p.is_file() else None,
                    "modified": p.stat().st_mtime
                })

        return {
            "directory": str(path),
            "files": files,
            "total_files": len(files)
        }

    except Exception as e:
        logger.error(f"Error listing directory {path}: {str(e)}")
        raise

@tool(
    name="read_file",
    description="Read contents of a file",
    category=ToolCategory.FILE_SYSTEM,
    parameters=[
        ToolParameter("path", str, "File path to read", True),
        ToolParameter("encoding", str, "File encoding", True)
    ]
)
async def read_file(path: str, encoding: str = "utf-8") -> Dict[str, Any]:
    """Read contents of a file"""
    try:
        path = Path(path)
        if not path.exists():
            raise FileNotFoundError(f"File not found: {path}")
        if not path.is_file():
            raise IsADirectoryError(f"Not a file: {path}")

        content = path.read_text(encoding=encoding)
        stats = path.stat()

        return {
            "path": str(path),
            "content": content,
            "size": stats.st_size,
            "modified": stats.st_mtime,
            "encoding": encoding
        }

    except Exception as e:
        logger.error(f"Error reading file {path}: {str(e)}")
        raise

@tool(
    name="write_file",
    description="Write contents to a file",
    category=ToolCategory.FILE_SYSTEM,
    parameters=[
        ToolParameter("path", str, "File path to write", True),
        ToolParameter("content", str, "Content to write", True),
        ToolParameter("encoding", str, "File encoding", True)
    ]
)
async def write_file(path: str, content: str, encoding: str = "utf-8") -> Dict[str, Any]:
    """Write contents to a file"""
    try:
        path = Path(path)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding=encoding)
        stats = path.stat()

        return {
            "path": str(path),
            "size": stats.st_size,
            "modified": stats.st_mtime,
            "encoding": encoding
        }

    except Exception as e:
        logger.error(f"Error writing file {path}: {str(e)}")
        raise

@tool(
    name="delete_file",
    description="Delete a file or directory",
    category=ToolCategory.FILE_SYSTEM,
    parameters=[
        ToolParameter("path", str, "Path to delete", True),
        ToolParameter("recursive", bool, "Delete recursively", True)
    ]
)
async def delete_file(path: str, recursive: bool = False) -> Dict[str, Any]:
    """Delete a file or directory"""
    try:
        path = Path(path)
        if not path.exists():
            raise FileNotFoundError(f"Path not found: {path}")

        was_directory = path.is_dir()
        if was_directory:
            if recursive:
                shutil.rmtree(path)
            else:
                path.rmdir()  # Will fail if directory is not empty
        else:
            path.unlink()

        return {
            "path": str(path),
            "type": "directory" if was_directory else "file",
            "recursive": recursive,
            "success": True
        }

    except Exception as e:
        logger.error(f"Error deleting {path}: {str(e)}")
        raise
