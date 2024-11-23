"""
Message bubble component for individual chat messages
"""

from PySide6.QtWidgets import QWidget, QLabel, QHBoxLayout
from PySide6.QtCore import Qt

class MessageBubble(QWidget):
    """
    Custom widget for rendering individual chat messages with proper styling
    """
    def __init__(self, text, is_user=False):
        super().__init__()
        
        # Create layout
        layout = QHBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        self.setLayout(layout)
        
        # Add spacing for alignment
        if is_user:
            layout.addStretch()
        
        # Create message label
        self.label = QLabel(text)
        self.label.setWordWrap(True)
        self.label.setTextFormat(Qt.TextFormat.PlainText)
        self.label.setTextInteractionFlags(
            Qt.TextSelectableByMouse | 
            Qt.TextSelectableByKeyboard
        )
        
        # Style label
        color = "#e8dcc8" if is_user else "#F8EFD8"
        self.label.setStyleSheet(f"""
            QLabel {{
                background: {color};
                border-radius: 16px;
                padding: 8px 12px;
                font-size: 14px;
                line-height: 1.4;
            }}
        """)
        layout.addWidget(self.label)
        
        # Add spacing for alignment
        if not is_user:
            layout.addStretch()

    def update_text(self, text):
        """Update the message text"""
        self.label.setText(text)
