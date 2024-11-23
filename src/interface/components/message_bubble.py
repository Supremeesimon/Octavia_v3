"""
Message bubble component for individual chat messages
"""

from PySide6.QtWidgets import QWidget, QLabel, QHBoxLayout, QSizePolicy
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
        
        # Add initial stretch for right alignment if user message
        if is_user:
            layout.addStretch()
        
        # Create message label
        self.label = QLabel(text)
        self.label.setWordWrap(True)  # Re-enable word wrap
        self.label.setTextFormat(Qt.TextFormat.PlainText)
        self.label.setTextInteractionFlags(
            Qt.TextSelectableByMouse | 
            Qt.TextSelectableByKeyboard
        )
        
        # Make label size policy fit content with max width
        self.label.setSizePolicy(QSizePolicy.Maximum, QSizePolicy.Preferred)
        self.label.setMaximumWidth(800)  # Good width for desktop
        
        # Style label
        color = "#e8dcc8" if is_user else "#eadfd0"  # Darker than before but still lighter than user
        self.label.setStyleSheet(f"""
            QLabel {{
                background: {color};
                border-radius: 16px;
                padding: 8px 12px;
                font-size: 14px;
                line-height: 1.4;
                selection-background-color: white;
                selection-color: #2C1810;
            }}
        """)
        
        # Add label to layout
        layout.addWidget(self.label)
        
        # Add final stretch for left alignment if Octavia message
        if not is_user:
            layout.addStretch()
            
    def update_text(self, text):
        """Update the message text"""
        self.label.setText(text)
        self.label.adjustSize()
