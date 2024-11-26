"""
Octavia's UI Observer - Non-intrusive UI monitoring and awareness integration
"""

from typing import Optional, Dict, Any
from PySide6.QtCore import QObject, Qt, Signal, QTimer
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
    
    def __init__(self, app, ui_awareness, main_window):
        try:
            super().__init__(main_window)  # Set parent for proper cleanup
            self.app = app
            self.ui_awareness = ui_awareness
            self.main_window = main_window
            self._last_event_time = datetime.now()
            self._event_throttle = 0.1  # seconds
            self.last_mouse_pos = None
            self.last_interaction_time = None
            self.hover_start_time = None
            self.current_widget = None
            
            # Initialize with a delay to ensure window is ready
            QTimer.singleShot(1000, self._delayed_init)
            logger.debug("UIObserver initialization scheduled")
            
        except Exception as e:
            logger.error(f"Error initializing UIObserver: {e}")
            # Don't raise, allow observer to initialize in limited capacity
    
    def _delayed_init(self):
        """Perform delayed initialization after window is ready"""
        try:
            if not self.main_window:
                logger.error("Main window not available for delayed initialization")
                return
                
            # Enable mouse tracking without modifying UI
            self.main_window.setAttribute(Qt.WA_MouseTracking, True)
            logger.debug("UIObserver delayed initialization complete")
            
        except Exception as e:
            logger.error(f"Error in delayed initialization: {e}")
        
    def _should_process_event(self) -> bool:
        """Check if enough time has passed to process another event"""
        now = datetime.now()
        if (now - self._last_event_time).total_seconds() < self._event_throttle:
            return False
        self._last_event_time = now
        return True
        
    def eventFilter(self, watched: QObject, event: QMouseEvent) -> bool:
        """Filter UI events for awareness"""
        try:
            if isinstance(event, QMouseEvent):
                pos = event.pos()
                context = {
                    'position': {'x': pos.x(), 'y': pos.y()},
                    'timestamp': datetime.now().isoformat(),
                    'widget': watched.objectName() if hasattr(watched, 'objectName') else None
                }
                self.interaction_detected.emit(context)
            return False  # Don't consume the event
        except Exception as e:
            logger.error(f"Error in event filter: {e}")
            return False
            
    def _handle_mouse_move(self, event: QMouseEvent):
        """Track mouse movement without UI modification"""
        try:
            current_pos = event.pos()
            current_time = datetime.now()
            
            # Basic movement tracking
            if self.last_mouse_pos:
                movement = current_pos - self.last_mouse_pos
                if movement.manhattanLength() > 5:  # Threshold for significant movement
                    self._emit_interaction("mouse_move", {
                        "position": (current_pos.x(), current_pos.y()),
                        "time": current_time.isoformat()
                    })
            
            self.last_mouse_pos = current_pos
            self.last_interaction_time = current_time
            
        except Exception as e:
            logger.error(f"Error handling mouse move: {e}")
    
    def _handle_mouse_click(self, event: QMouseEvent):
        """Handle mouse click events"""
        try:
            click_pos = event.pos()
            self._emit_interaction("mouse_click", {
                "position": (click_pos.x(), click_pos.y()),
                "button": event.button(),
                "time": datetime.now().isoformat()
            })
        except Exception as e:
            logger.error(f"Error handling mouse click: {e}")
    
    def _emit_interaction(self, interaction_type: str, data: Dict[str, Any]):
        """Safely emit interaction events"""
        try:
            self.interaction_detected.emit({
                "type": interaction_type,
                "data": data,
                "timestamp": datetime.now().isoformat()
            })
        except Exception as e:
            logger.error(f"Error emitting interaction: {e}")

    def update_mouse_context(self, event) -> None:
        """Update mouse context from event"""
        try:
            # Throttle event processing
            if not self._should_process_event():
                return
                
            widget = self.app.widgetAt(event.globalPos())
            if not widget:
                return
                
            # Safely get widget type
            try:
                widget_type = type(widget).__name__
            except:
                widget_type = "Unknown"
                
            context = {
                "position": event.pos(),
                "global_position": event.globalPos(),
                "widget": widget,
                "widget_type": widget_type,
                "timestamp": datetime.now()
            }
            
            self.ui_awareness.update_mouse_context(context)
            
        except Exception as e:
            logger.error(f"Error updating mouse context: {e}")
            # Don't re-raise, just log the error
