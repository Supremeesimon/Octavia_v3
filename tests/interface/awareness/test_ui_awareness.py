"""
Tests for Octavia's UI Awareness System
"""

import pytest
from unittest.mock import Mock, MagicMock, patch
from PySide6.QtCore import Qt
from interface.awareness.ui_awareness import UIAwarenessSystem, MouseContext, UIState

@pytest.fixture
def mock_brain():
    """Create a mock brain instance"""
    brain = MagicMock()
    brain.update_interaction_context = MagicMock()
    brain._consider_contextual_response = MagicMock()
    return brain

@pytest.fixture
def ui_awareness():
    """Create UI awareness instance"""
    awareness = UIAwarenessSystem()
    return awareness

def test_mouse_context_update(ui_awareness):
    """Test updating mouse context"""
    # Setup test context
    context = {
        "position": MagicMock(),
        "widget_type": "ChatDisplay",
        "widget_area": "main",
        "hovering_message": True,
        "near_input": False,
    }
    
    # Update context
    ui_awareness.update_mouse_context(context)
    
    # Verify
    assert ui_awareness.mouse_context is not None
    assert ui_awareness.mouse_context.widget_type == "ChatDisplay"
    assert ui_awareness.mouse_context.hovering_message is True

def test_ui_state_update(ui_awareness):
    """Test updating UI state"""
    # Setup test state
    state_updates = {
        "scroll_position": 500,
        "visible_messages": ["msg1", "msg2"],
        "user_attention_area": "chat"
    }
    
    # Update state
    ui_awareness.update_ui_state(state_updates)
    
    # Verify
    assert ui_awareness.ui_state.scroll_position == 500
    assert len(ui_awareness.ui_state.visible_messages) == 2
    assert ui_awareness.ui_state.user_attention_area == "chat"

def test_interaction_history(ui_awareness):
    """Test interaction history management"""
    # Add several state updates
    for i in range(5):
        ui_awareness.update_ui_state({
            "scroll_position": i * 100
        })
    
    # Verify history is maintained
    assert len(ui_awareness.interaction_history) == 5
    assert ui_awareness.interaction_history[-1]["state_change"]["scroll_position"] == 400

def test_hover_suggestions(ui_awareness):
    """Test hover-based suggestions"""
    # Setup hovering context
    context = {
        "position": MagicMock(),
        "widget_type": "MessageBubble",
        "widget_area": "chat",
        "hovering_message": True,
        "near_input": False
    }
    
    # Simulate long hover
    ui_awareness.update_mouse_context(context)
    ui_awareness.mouse_context.hover_duration = 2.5  # seconds
    
    # Get suggestions
    suggestions = ui_awareness.get_interaction_suggestions()
    
    # Verify suggestions were generated
    assert len(suggestions) > 0
    assert any("message" in s.lower() for s in suggestions)
