"""
Tests for Octavia's UI Observer
"""

import pytest
from unittest.mock import Mock, MagicMock
from PySide6.QtCore import Qt, QPoint
from PySide6.QtGui import QMouseEvent
from PySide6.QtWidgets import QMainWindow, QWidget
from interface.awareness.ui_observer import UIObserver

@pytest.fixture
def mock_main_window():
    """Create a mock main window"""
    window = MagicMock(spec=QMainWindow)
    window.chat_display = MagicMock()
    window.chat_display.verticalScrollBar = MagicMock(return_value=MagicMock())
    return window

@pytest.fixture
def ui_observer(mock_main_window):
    """Create UI observer instance"""
    observer = UIObserver(mock_main_window)
    return observer

def create_mouse_event(event_type, pos, button=Qt.LeftButton):
    """Helper to create mouse events"""
    point = QPoint(*pos)
    return QMouseEvent(
        event_type,
        point,  # localPos
        point,  # windowPos (same as localPos for our tests)
        point,  # screenPos (same as localPos for our tests)
        button,
        button,
        Qt.NoModifier,
        Qt.MouseEventSource.MouseEventNotSynthesized
    )

def test_mouse_move_tracking(ui_observer, mock_main_window):
    """Test mouse movement tracking"""
    # Setup
    mock_widget = MagicMock(spec=QWidget)
    mock_widget.__class__.__name__ = "ChatDisplay"
    mock_main_window.childAt.return_value = mock_widget
    
    # Create signal spy
    signal_spy = []
    ui_observer.interaction_detected.connect(lambda x: signal_spy.append(x))
    
    # Simulate mouse move
    event = create_mouse_event(QMouseEvent.MouseMove, (100, 100))
    ui_observer.eventFilter(mock_main_window, event)
    
    # Verify
    assert len(signal_spy) == 1
    context = signal_spy[0]
    assert context["event_type"] == "mouse_move"
    assert context["widget_type"] == "ChatDisplay"
    assert "position" in context
    assert "timestamp" in context

def test_mouse_click_detection(ui_observer, mock_main_window):
    """Test mouse click detection"""
    # Setup
    mock_widget = MagicMock(spec=QWidget)
    mock_widget.__class__.__name__ = "MessageBubble"
    mock_main_window.childAt.return_value = mock_widget
    
    # Create signal spy
    signal_spy = []
    ui_observer.interaction_detected.connect(lambda x: signal_spy.append(x))
    
    # Simulate click
    event = create_mouse_event(QMouseEvent.MouseButtonPress, (150, 150))
    ui_observer.eventFilter(mock_main_window, event)
    
    # Verify
    assert len(signal_spy) == 1
    context = signal_spy[0]
    assert context["event_type"] == "mouse_click"
    assert context["widget_type"] == "MessageBubble"
    assert context["button"] == Qt.LeftButton

def test_hover_duration_tracking(ui_observer, mock_main_window):
    """Test hover duration tracking"""
    # Setup
    mock_widget = MagicMock(spec=QWidget)
    mock_widget.__class__.__name__ = "TextInput"
    mock_main_window.childAt.return_value = mock_widget
    
    # Create signal spy
    signal_spy = []
    ui_observer.interaction_detected.connect(lambda x: signal_spy.append(x))
    
    # Simulate hover (multiple small movements)
    for i in range(5):
        event = create_mouse_event(QMouseEvent.MouseMove, (200 + i, 200))
        ui_observer.eventFilter(mock_main_window, event)
    
    # Verify increasing hover duration
    assert len(signal_spy) > 0
    hover_durations = [
        c.get("hover_duration", 0) 
        for c in signal_spy 
        if c["event_type"] == "mouse_move"
    ]
    # Verify hover was detected
    assert any(d > 0 for d in hover_durations)

def test_scroll_tracking(ui_observer, mock_main_window):
    """Test scroll behavior tracking"""
    # Setup
    scrollbar = mock_main_window.chat_display.verticalScrollBar()
    scrollbar.maximum.return_value = 1000
    
    # Create signal spy
    signal_spy = []
    ui_observer.interaction_detected.connect(lambda x: signal_spy.append(x))
    
    # Simulate scroll
    ui_observer._handle_scroll(500)
    
    # Verify
    assert len(signal_spy) == 1
    context = signal_spy[0]
    assert context["event_type"] == "scroll"
    assert context["position"] == 500
    assert context["max_scroll"] == 1000

def test_widget_area_detection(ui_observer, mock_main_window):
    """Test correct detection of widget areas"""
    # Setup left panel widget
    left_widget = MagicMock(spec=QWidget)
    left_widget.__class__.__name__ = "LeftPanel"
    left_widget.objectName.return_value = "leftContainer"
    mock_main_window.childAt.return_value = left_widget
    
    # Create signal spy
    signal_spy = []
    ui_observer.interaction_detected.connect(lambda x: signal_spy.append(x))
    
    # Simulate interaction
    event = create_mouse_event(QMouseEvent.MouseMove, (50, 100))
    ui_observer.eventFilter(mock_main_window, event)
    
    # Verify
    assert len(signal_spy) == 1
    context = signal_spy[0]
    assert context["widget_area"] == "left_panel"
