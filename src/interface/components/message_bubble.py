"""
Message bubble component for individual chat messages
"""

from PySide6.QtWidgets import QWidget, QLabel, QHBoxLayout, QVBoxLayout, QSizePolicy, QPushButton
from PySide6.QtCore import Qt, QDateTime, QSize
from PySide6.QtGui import QIcon, QGuiApplication
import markdown
import os

class MessageBubble(QWidget):
    """
    Custom widget for rendering individual chat messages with proper styling
    """
    def __init__(self, text, is_user=False):
        super().__init__()
        
        # Store the raw text for copying
        self.raw_text = text
        
        # Create main layout
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(2)  # Small gap between message and timestamp
        self.setLayout(main_layout)
        
        # Create message layout
        msg_layout = QHBoxLayout()
        msg_layout.setContentsMargins(0, 0, 0, 0)
        
        # Add initial stretch for right alignment if user message
        if is_user:
            msg_layout.addStretch()
        
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
        
        # Style message label
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
        
        # Add message label to layout
        msg_layout.addWidget(self.label)
        
        # Add final stretch for left alignment if Octavia message
        if not is_user:
            msg_layout.addStretch()
        
        # Create timestamp layout with copy button
        time_layout = QHBoxLayout()
        time_layout.setContentsMargins(8, 0, 8, 0)  # Add some horizontal padding
        time_layout.setSpacing(4)  # Small gap between timestamp and copy button
        
        # Add initial stretch for right alignment if user message
        if is_user:
            time_layout.addStretch()
        
        # Create and style timestamp label
        current_time = QDateTime.currentDateTime().toString("hh:mm AP")
        self.time_label = QLabel(current_time)
        self.time_label.setStyleSheet("""
            QLabel {
                color: #666666;
                font-size: 11px;
                font-style: italic;
            }
        """)
        
        # Create copy button
        copy_button = QPushButton()
        copy_button.setFixedSize(12, 12)  # Make it smaller
        copy_button.setCursor(Qt.PointingHandCursor)
        copy_button.setToolTip("Copy message")
        
        # Load copy icon
        icon_path = os.path.join(os.path.dirname(__file__), "icons", "copy.svg")
        if os.path.exists(icon_path):
            icon = QIcon(icon_path)
            copy_button.setIcon(icon)
            copy_button.setIconSize(QSize(10, 10))  # Slightly smaller icon
        
        # Style copy button to match timestamp
        copy_button.setStyleSheet("""
            QPushButton {
                background-color: transparent;
                border: none;
                padding: 0px;
            }
            QPushButton:hover {
                background-color: rgba(0, 0, 0, 0.05);
                border-radius: 2px;
            }
        """)
        
        copy_button.clicked.connect(self._copy_text)
        
        # Add timestamp and copy button to layout
        if is_user:
            time_layout.addWidget(copy_button)
            time_layout.addWidget(self.time_label)
        else:
            time_layout.addWidget(self.time_label)
            time_layout.addWidget(copy_button)
        
        # Add final stretch for left alignment if Octavia message
        if not is_user:
            time_layout.addStretch()
        
        # Add both layouts to main layout
        main_layout.addLayout(msg_layout)
        main_layout.addLayout(time_layout)
            
    def update_text(self, text):
        """Update the message text"""
        self.raw_text = text
        html_text = markdown.markdown(text, extensions=['nl2br'])
        self.label.setText(html_text)
        self.label.adjustSize()
        
        # Update timestamp
        current_time = QDateTime.currentDateTime().toString("hh:mm AP")
        self.time_label.setText(current_time)
        
    def _copy_text(self):
        """Copy the raw message text to clipboard"""
        clipboard = QGuiApplication.clipboard()
        clipboard.setText(self.raw_text)
