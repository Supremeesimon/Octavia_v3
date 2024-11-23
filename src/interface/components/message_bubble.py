"""
Message bubble component for individual chat messages
"""

from PySide6.QtWidgets import QWidget, QLabel, QHBoxLayout, QSizePolicy
from PySide6.QtCore import Qt
import markdown

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
        
        # Convert markdown to HTML with minimal formatting
        html_text = markdown.markdown(text, extensions=['nl2br'])
        
        # Create message label
        self.label = QLabel(html_text)
        self.label.setWordWrap(True)
        self.label.setTextFormat(Qt.TextFormat.RichText)
        self.label.setTextInteractionFlags(
            Qt.TextSelectableByMouse | 
            Qt.TextSelectableByKeyboard
        )
        
        # Make label size policy fit content with max width
        self.label.setSizePolicy(QSizePolicy.Maximum, QSizePolicy.Preferred)
        self.label.setMaximumWidth(800)  # Good width for desktop
        
        # Style label
        color = "#e8dcc8" if is_user else "#eadfd0"
        self.label.setStyleSheet(f"""
            QLabel {{
                background: {color};
                border-radius: 16px;
                padding: 8px 12px;
                font-size: 14px;
                line-height: 1.4;
                selection-background-color: rgba(255, 255, 255, 0.4);
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
        html_text = markdown.markdown(text, extensions=['nl2br'])
        self.label.setText(html_text)
        self.label.adjustSize()
