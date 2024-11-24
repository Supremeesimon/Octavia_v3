"""
Chat display component for rendering messages
"""

from PySide6.QtWidgets import QScrollArea, QWidget, QVBoxLayout, QApplication
from PySide6.QtCore import Qt, QTimer
from .message_bubble import MessageBubble
from loguru import logger

class ChatDisplay(QScrollArea):
    """
    Display area for chat messages with custom styling
    """
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_ui()
        self.current_message_bubble = None
        
    def setup_ui(self):
        """Initialize the UI components"""
        # Create container widget and layout
        self.container = QWidget()
        self.layout = QVBoxLayout(self.container)
        self.layout.setContentsMargins(20, 20, 20, 20)
        self.layout.setSpacing(12)
        self.layout.addStretch()
        
        # Set up scroll area
        self.setWidget(self.container)
        self.setWidgetResizable(True)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        
        # Style scroll area
        self.setStyleSheet("""
            QScrollArea {
                border: none;
                background: transparent;
            }
            QWidget {
                background: transparent;
            }
        """)
    
    def add_message(self, text, is_user=False):
        """Add a new message bubble"""
        try:
            # Remove stretch
            self.layout.takeAt(self.layout.count() - 1)
            
            # Create new message bubble
            bubble = MessageBubble(text, is_user)
            self.layout.addWidget(bubble)
            self.current_message_bubble = bubble
            
            # Add stretch back
            self.layout.addStretch()
            
            # Scroll to bottom
            QTimer.singleShot(100, self._ensure_scrolled_to_bottom)
            
        except Exception as e:
            logger.error(f"Error adding message: {str(e)}")
            
    def update_last_message(self, text):
        """Update the text of the last message bubble"""
        if self.current_message_bubble:
            self.current_message_bubble.update_text(text)
            QTimer.singleShot(100, self._ensure_scrolled_to_bottom)
            
    def finish_message(self):
        """Mark the current message as finished"""
        if self.current_message_bubble:
            self.current_message_bubble.finish()
            self.current_message_bubble = None
    
    def append_system_message(self, text):
        """Add a system message (like errors or status updates)"""
        # Remove stretch
        self.layout.takeAt(self.layout.count() - 1)
        
        # Create new message bubble for system message
        message_bubble = MessageBubble(text, is_user=False)
        self.layout.addWidget(message_bubble)
        
        # Add stretch back
        self.layout.addStretch()
        
        # Scroll to bottom
        self._ensure_scrolled_to_bottom()
    
    def _ensure_scrolled_to_bottom(self):
        """Ensure the chat is scrolled to the latest message"""
        self.verticalScrollBar().setValue(
            self.verticalScrollBar().maximum()
        )
