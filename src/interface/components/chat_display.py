"""
Chat display component for rendering messages
"""

from PySide6.QtWidgets import QScrollArea, QWidget, QVBoxLayout
from PySide6.QtCore import Qt
from .message_bubble import MessageBubble

class ChatDisplay(QScrollArea):
    """
    Scrollable container for chat messages with proper alignment and spacing
    """
    def __init__(self):
        super().__init__()
        self.setWidgetResizable(True)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        
        # Container widget
        self.container = QWidget()
        self.setWidget(self.container)
        
        # Layout
        self.layout = QVBoxLayout()
        self.layout.setSpacing(8)
        self.layout.setContentsMargins(8, 8, 8, 8)
        self.layout.addStretch()
        self.container.setLayout(self.layout)
        
        # Keep track of current message for typewriter effect
        self.current_message_bubble = None
        
        # Style
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
        # Remove stretch
        self.layout.takeAt(self.layout.count() - 1)
        
        # Create new bubble or update existing
        if not self.current_message_bubble:
            self.current_message_bubble = MessageBubble(text, is_user)
            self.layout.addWidget(self.current_message_bubble)
        else:
            # Update existing bubble text
            self.current_message_bubble.update_text(text)
        
        # Add stretch back
        self.layout.addStretch()
        
        # Scroll to bottom
        self.verticalScrollBar().setValue(
            self.verticalScrollBar().maximum()
        )
        self.verticalScrollBar().setValue(
            self.verticalScrollBar().maximum()
        )

    def finish_message(self):
        """Mark current message as complete"""
        self.current_message_bubble = None
