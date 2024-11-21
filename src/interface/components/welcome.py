"""
Welcome section component for Octavia
"""

from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel
from PySide6.QtCore import Qt

class WelcomeSection(QWidget):
    """Welcome section with title and description"""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_ui()

    def setup_ui(self):
        """Setup the welcome section UI"""
        layout = QVBoxLayout(self)
        layout.setSpacing(12)
        layout.setContentsMargins(40, 40, 0, 0)  

        # Title
        title = QLabel("Manage your folders with Octavia")
        title.setObjectName("welcomeTitle")
        title.setStyleSheet("font-size: 28px; font-weight: bold; color: #4a4a4a;")
        title.setAlignment(Qt.AlignLeft)  
        layout.addWidget(title)

        # Description
        description = QLabel("Kick off a new project or organize your files")
        description.setObjectName("welcomeDescription")
        description.setStyleSheet("font-size: 18px; color: #666666;")
        description.setWordWrap(True)
        description.setAlignment(Qt.AlignLeft)  
        layout.addWidget(description)

        # Hint
        hint = QLabel("New to Octavia? Try it out with a test workspace")
        hint.setStyleSheet("font-size: 14px; color: #888888;")
        hint.setAlignment(Qt.AlignLeft)
        layout.addWidget(hint)

        # Add stretch to push content to top
        layout.addStretch()
