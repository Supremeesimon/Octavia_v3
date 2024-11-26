"""
Octavia's UI Awareness System - Tracks and manages UI state and interactions
"""

from dataclasses import dataclass
from datetime import datetime
from typing import Optional, Dict, Any, List, Tuple, Union
from PySide6.QtCore import QPoint
from loguru import logger

@dataclass
class MouseContext:
    """Track mouse-related context"""
    position: QPoint
    widget_type: str
    widget_area: str
    hovering_message: bool
    near_input: bool
    last_interaction: datetime
    hover_duration: float = 0.0

@dataclass
class UIState:
    """Track overall UI state"""
    scroll_position: int = 0
    visible_messages: List[str] = None
    user_attention_area: str = None
    last_click_position: Optional[QPoint] = None
    window_state: str = "normal"
    layout_mode: str = "chat"

class UIAwarenessSystem:
    """Manages Octavia's awareness of UI state and interactions"""
    
    def __init__(self):
        self.mouse_context = None
        self.ui_state = UIState()
        self.visible_messages = []  # Initialize visible messages list
        self.interaction_history = []
        self.attention_patterns = {}
        self._abilities = {}
        self._register_default_abilities()
        
    def _register_default_abilities(self):
        """Register default UI abilities"""
        # Add base abilities 
        self.register_ability("register_ability", self.register_ability, "Register new UI ability")
            
    def register_ability(self, ability_name: str, handler: callable, description: str = None) -> bool:
        """Register a UI ability"""
        try:
            if not hasattr(handler, '__call__'):
                logger.error(f"Handler for {ability_name} must be callable")
                return False
                
            self._abilities[ability_name] = {
                'handler': handler,
                'enabled': True,
                'description': description or f'UI ability: {ability_name}'
            }
            logger.info(f"Registered UI ability: {ability_name}")
            return True
        except Exception as e:
            logger.error(f"Error registering ability {ability_name}: {e}")
            return False
            
    def get_ability(self, name: str) -> dict:
        """Get a registered ability by name"""
        return self._abilities.get(name)
            
    def update_mouse_context(self, context: dict):
        """Update mouse context information"""
        try:
            if not isinstance(context, dict):
                logger.warning(f"Invalid context type: {type(context)}")
                return
                
            # Extract mouse position if available
            mouse_pos = context.get('mouse_position', {})
            if isinstance(mouse_pos, dict):
                x = mouse_pos.get('x', 0)
                y = mouse_pos.get('y', 0)
                self.mouse_context = MouseContext(
                    position=QPoint(x, y),
                    widget_type=context.get("widget_type", "unknown"),
                    widget_area=context.get("widget_area", "unknown"),
                    hovering_message=context.get("hovering_message", False),
                    near_input=context.get("near_input", False),
                    last_interaction=datetime.now(),
                    hover_duration=0.0
                )
            else:
                logger.warning(f"Invalid mouse_position type: {type(mouse_pos)}")
                
        except Exception as e:
            logger.error(f"Error updating mouse context: {e}")
    
    def update_ui_state(self, state_updates: Dict[str, Any]) -> None:
        """Update UI state with new information"""
        try:
            for key, value in state_updates.items():
                if hasattr(self.ui_state, key):
                    setattr(self.ui_state, key, value)
            
            # Track state changes
            self.interaction_history.append({
                "timestamp": datetime.now(),
                "state_change": state_updates
            })
            
            # Cleanup old history (keep last 100 interactions)
            if len(self.interaction_history) > 100:
                self.interaction_history = self.interaction_history[-100:]
                
        except Exception as e:
            logger.error(f"Error updating UI state: {e}")
    
    def get_interaction_suggestions(self) -> List[str]:
        """Generate contextual suggestions based on current state"""
        suggestions = []
        
        try:
            # Check hover patterns
            if self.mouse_context and self.mouse_context.hover_duration > 2.0:
                if self.mouse_context.hovering_message:
                    suggestions.append("I notice you're looking at this message. Would you like me to explain it further?")
                elif self.mouse_context.near_input:
                    suggestions.append("Looking to type something? I'm ready to help!")
                    
            # Check scroll position
            if self.ui_state.scroll_position > 0:
                suggestions.append("I see you're looking at our earlier conversation. Need any context from previous messages?")
                
            # Check window state
            if self.ui_state.window_state == "normal" and len(self.visible_messages) > 10:
                suggestions.append("Would you like me to adjust my window size to show more of our conversation?")
                
        except Exception as e:
            logger.error(f"Error generating interaction suggestions: {e}")
            
        return suggestions
    
    def _is_similar_position(self, new_pos: QPoint, threshold: int = 5) -> bool:
        """Check if new position is similar to current position"""
        if not self.mouse_context or not self.mouse_context.position:
            return False
        
        dx = abs(new_pos.x() - self.mouse_context.position.x())
        dy = abs(new_pos.y() - self.mouse_context.position.y())
        return dx <= threshold and dy <= threshold
    
    def _log_hover_pattern(self) -> None:
        """Log significant hover patterns for learning"""
        if not self.mouse_context:
            return
            
        pattern_key = f"{self.mouse_context.widget_area}_{self.mouse_context.widget_type}"
        if pattern_key not in self.attention_patterns:
            self.attention_patterns[pattern_key] = []
            
        self.attention_patterns[pattern_key].append({
            "timestamp": datetime.now(),
            "duration": self.mouse_context.hover_duration,
            "context": {
                "widget_area": self.mouse_context.widget_area,
                "widget_type": self.mouse_context.widget_type,
                "ui_state": self.ui_state
            }
        })

    @property
    def abilities(self):
        """Get all registered abilities"""
        return self._abilities
