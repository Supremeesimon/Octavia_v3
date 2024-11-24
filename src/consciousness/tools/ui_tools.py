"""
UI manipulation tools for Octavia.
"""

from typing import Dict, List, Optional, Any
from loguru import logger
from PySide6.QtWidgets import QWidget, QMainWindow
from PySide6.QtCore import Qt, QPoint, QRect

from .tool_system import tool, ToolCategory, ToolParameter

@tool(
    name="get_window_info",
    description="Get information about a window",
    category=ToolCategory.UI,
    parameters=[
        ToolParameter("window", QWidget, "Window to get info about", True),
    ]
)
async def get_window_info(window: QWidget) -> Dict[str, Any]:
    """Get information about a window"""
    try:
        geometry = window.geometry()
        return {
            "class": window.__class__.__name__,
            "title": window.windowTitle(),
            "geometry": {
                "x": geometry.x(),
                "y": geometry.y(),
                "width": geometry.width(),
                "height": geometry.height()
            },
            "visible": window.isVisible(),
            "enabled": window.isEnabled(),
            "window_state": window.windowState(),
            "window_flags": int(window.windowFlags()),
        }
    except Exception as e:
        logger.error(f"Error getting window info: {str(e)}")
        raise

@tool(
    name="set_window_geometry",
    description="Set window geometry",
    category=ToolCategory.UI,
    parameters=[
        ToolParameter("window", QWidget, "Window to modify", True),
        ToolParameter("x", int, "X coordinate", True),
        ToolParameter("y", int, "Y coordinate", True),
        ToolParameter("width", int, "Width", True),
        ToolParameter("height", int, "Height", True),
    ]
)
async def set_window_geometry(window: QWidget, x: int, y: int, width: int, height: int) -> None:
    """Set window geometry"""
    try:
        window.setGeometry(x, y, width, height)
    except Exception as e:
        logger.error(f"Error setting window geometry: {str(e)}")
        raise

@tool(
    name="set_window_state",
    description="Set window state",
    category=ToolCategory.UI,
    parameters=[
        ToolParameter("window", QWidget, "Window to modify", True),
        ToolParameter("state", str, "Window state (normal, minimized, maximized, fullscreen)", True),
    ]
)
async def set_window_state(window: QWidget, state: str) -> None:
    """Set window state"""
    try:
        state = state.lower()
        if state == "normal":
            window.setWindowState(Qt.WindowNoState)
        elif state == "minimized":
            window.setWindowState(Qt.WindowMinimized)
        elif state == "maximized":
            window.setWindowState(Qt.WindowMaximized)
        elif state == "fullscreen":
            window.setWindowState(Qt.WindowFullScreen)
        else:
            raise ValueError(f"Invalid window state: {state}")
    except Exception as e:
        logger.error(f"Error setting window state: {str(e)}")
        raise

@tool(
    name="find_child_widgets",
    description="Find child widgets of a given type",
    category=ToolCategory.UI,
    parameters=[
        ToolParameter("parent", QWidget, "Parent widget", True),
        ToolParameter("widget_type", str, "Type of widget to find", True),
        ToolParameter("name_filter", str, "Filter by object name", False, None),
    ]
)
async def find_child_widgets(parent: QWidget, widget_type: str, name_filter: Optional[str] = None) -> List[QWidget]:
    """Find child widgets of a given type"""
    try:
        widgets = []
        for child in parent.findChildren(QWidget):
            if child.__class__.__name__ == widget_type:
                if name_filter is None or name_filter in child.objectName():
                    widgets.append(child)
        return widgets
    except Exception as e:
        logger.error(f"Error finding child widgets: {str(e)}")
        raise
