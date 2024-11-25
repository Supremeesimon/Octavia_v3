"""
Octavia's UI Observer - Non-intrusive UI monitoring and awareness integration
"""

from typing import Optional, Dict, Any
from PySide6.QtCore import QObject, Qt, Signal
from PySide6.QtGui import QMouseEvent
from datetime import datetime
import asyncio
from loguru import logger

class UIObserver(QObject):
    """
    Observes UI interactions without modifying existing UI
    Acts as a bridge between UI events and Octavia's awareness system
    """
    
    interaction_detected = Signal(dict)  # Emits interaction context
    
    def __init__(self, main_window):
        super().__init__()
        self.main_window = main_window
        self.last_mouse_pos = None
        self.last_interaction_time = None
        self.hover_start_time = None
        self.current_widget = None
        
        # Enable mouse tracking without modifying UI
        self.main_window.setAttribute(Qt.WA_MouseTracking, True)
        
        # Connect to existing signals if available
        if hasattr(main_window, 'chat_display'):
            self._connect_chat_signals()
            
    def eventFilter(self, watched: QObject, event: QMouseEvent) -> bool:
        """Filter UI events without interfering with normal operation"""
        try:
            if event.type() == QMouseEvent.MouseMove:
                self._handle_mouse_move(event)
            elif event.type() == QMouseEvent.MouseButtonPress:
                self._handle_mouse_click(event)
                
            # Let event continue normal processing
            return False
            
        except Exception as e:
            logger.error(f"Error in event filter: {e}")
            return False
            
    def _handle_mouse_move(self, event: QMouseEvent):
        """Track mouse movement without UI modification"""
        current_pos = event.position().toPoint()
        current_time = datetime.now()
        
        # Get widget under mouse without UI changes
        widget = self.main_window.childAt(current_pos)
        widget_info = self._get_widget_info(widget)
        
        context = {
            "position": current_pos,
            "widget_type": widget_info.get("type"),
            "widget_area": widget_info.get("area"),
            "timestamp": current_time,
            "event_type": "mouse_move"
        }
        
        # Calculate hover duration if mouse is relatively still
        if self._is_mouse_still(current_pos):
            if not self.hover_start_time:
                self.hover_start_time = current_time
            context["hover_duration"] = (current_time - self.hover_start_time).total_seconds()
        else:
            self.hover_start_time = current_time
            
        self.interaction_detected.emit(context)
        
    def _handle_mouse_click(self, event: QMouseEvent):
        """Track mouse clicks without UI modification"""
        click_pos = event.position().toPoint()
        widget = self.main_window.childAt(click_pos)
        widget_info = self._get_widget_info(widget)
        
        context = {
            "position": click_pos,
            "widget_type": widget_info.get("type"),
            "widget_area": widget_info.get("area"),
            "timestamp": datetime.now(),
            "event_type": "mouse_click",
            "button": event.button()
        }
        
        self.interaction_detected.emit(context)
        
    def _get_widget_info(self, widget: Optional[QObject]) -> Dict[str, str]:
        """Get widget information without modifying UI structure"""
        if not widget:
            return {"type": "none", "area": "none"}
            
        # Identify widget type and area based on existing UI structure
        widget_type = widget.__class__.__name__
        widget_area = "unknown"
        
        # Check parent hierarchy without modification
        parent = widget
        while parent:
            if parent.objectName() == "leftContainer":
                widget_area = "left_panel"
                break
            elif hasattr(parent, "chat_display"):
                widget_area = "chat_area"
                break
            parent = parent.parent()
            
        return {
            "type": widget_type,
            "area": widget_area
        }
        
    def _is_mouse_still(self, current_pos, threshold: int = 5) -> bool:
        """Check if mouse has moved significantly"""
        if not self.last_mouse_pos:
            self.last_mouse_pos = current_pos
            return True
            
        dx = abs(current_pos.x() - self.last_mouse_pos.x())
        dy = abs(current_pos.y() - self.last_mouse_pos.y())
        
        self.last_mouse_pos = current_pos
        return dx <= threshold and dy <= threshold
        
    def _connect_chat_signals(self):
        """Connect to existing chat signals without modification"""
        try:
            if hasattr(self.main_window.chat_display, 'verticalScrollBar'):
                scrollbar = self.main_window.chat_display.verticalScrollBar()
                scrollbar.valueChanged.connect(self._handle_scroll)
                
        except Exception as e:
            logger.error(f"Error connecting chat signals: {e}")
            
    def _handle_scroll(self, value: int):
        """Track scroll behavior without UI changes"""
        context = {
            "event_type": "scroll",
            "position": value,
            "timestamp": datetime.now(),
            "max_scroll": self.main_window.chat_display.verticalScrollBar().maximum()
        }
        
        self.interaction_detected.emit(context)
