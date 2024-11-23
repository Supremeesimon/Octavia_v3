"""
Left panel component for Octavia
"""

from PySide6.QtWidgets import (QWidget, QVBoxLayout, QPushButton, 
                             QLabel, QLineEdit, QHBoxLayout)
from PySide6.QtCore import Qt, Signal
from .status_dot import PulsingDot

class LeftPanel(QWidget):
    """Left panel component"""
    
    api_key_inserted = Signal(str)    # Emitted when API key is inserted
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("leftPanel")
        self.setFixedWidth(300)
        self.setAttribute(Qt.WA_TranslucentBackground)  # Make panel transparent
        self.setup_ui()
        
    def setup_ui(self):
        """Setup the left panel UI"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(16)
        
        # Header section
        header = QLabel("Workspaces")
        header.setObjectName("sidebarHeader")
        layout.addWidget(header)
        
        # Add stretch to push API key section to bottom
        layout.addStretch()
        
        # API Key section
        self.api_key_input = QLineEdit()
        self.api_key_input.setObjectName("apiKeyInput")
        self.api_key_input.setPlaceholderText("Enter activation key...")
        self.api_key_input.setEchoMode(QLineEdit.Password)
        layout.addWidget(self.api_key_input)
        
        self.insert_key_btn = QPushButton("Insert")
        self.insert_key_btn.setObjectName("insertKeyButton")
        self.insert_key_btn.clicked.connect(self._handle_key_insert)
        layout.addWidget(self.insert_key_btn)
        
        # Status section with dot and text
        status_layout = QHBoxLayout()
        status_layout.setSpacing(4)
        status_layout.setContentsMargins(0, 0, 0, 0)
        
        # Create container for dot
        dot_container = QWidget()
        dot_container.setFixedSize(30, 30)
        dot_container.setAttribute(Qt.WA_TranslucentBackground)
        dot_layout = QVBoxLayout(dot_container)
        dot_layout.setContentsMargins(0, 0, 0, 0)
        
        # Create the status dot
        self.status_dot = PulsingDot(self)
        dot_layout.addWidget(self.status_dot, 0, Qt.AlignCenter)
        
        # Create container for text
        text_container = QWidget()
        text_container.setAttribute(Qt.WA_TranslucentBackground)
        text_container.setFixedHeight(30)
        text_layout = QVBoxLayout(text_container)  
        text_layout.setContentsMargins(0, 0, 0, 0)
        
        # Configure text
        self.api_status = QLabel("")
        self.api_status.setObjectName("apiKeyStatus")
        self.api_status.setAttribute(Qt.WA_TranslucentBackground)
        font = self.api_status.font()
        font.setPointSize(13)
        self.api_status.setFont(font)
        self.api_status.setStyleSheet("color: rgba(0, 0, 0, 0.45);")
        text_layout.addWidget(self.api_status, 0, Qt.AlignCenter)
        
        # Add containers to main layout with baseline alignment
        status_layout.addWidget(dot_container, 0, Qt.AlignVCenter)
        status_layout.addWidget(text_container, 0, Qt.AlignVCenter)
        status_layout.addStretch()
        
        layout.addLayout(status_layout)
        
        # Initially hide status
        self.api_status.hide()
        self.status_dot.hide()
        
    def _handle_key_insert(self):
        """Handle API key insertion"""
        key = self.api_key_input.text().strip()
        if key:
            # Show status elements before emitting
            self.status_dot.show()
            self.api_status.show()
            self.status_dot.set_error()  # Start with error state
            self.api_status.setText("Validating...")
            # Emit the key for validation
            self.api_key_inserted.emit(key)
            
    def set_api_success(self):
        """Show API key success state"""
        # Update UI elements
        self.api_key_input.clear()
        self.api_key_input.setEnabled(False)
        self.insert_key_btn.hide()
        
        # Set status dot to success state
        self.status_dot.set_success()
        
        # Update status text
        self.api_status.setStyleSheet("color: rgba(0, 0, 0, 0.45);")
        self.api_status.setText("✓ API key activated")
        
        # Show status elements
        self.status_dot.show()
        self.api_status.show()

    def set_api_error(self, error_message: str = None):
        """Show API key error state"""
        # Reset UI elements
        self.api_key_input.clear()
        self.api_key_input.setEnabled(True)
        self.api_key_input.setFocus()
        self.insert_key_btn.show()
        
        # Set status dot to error state
        self.status_dot.set_error()
        
        # Update status text
        self.api_status.setStyleSheet("color: rgba(0, 0, 0, 0.45);")
        
        # Set appropriate error message
        if error_message and "quota" in error_message.lower():
            self.api_status.setText("API quota exceeded")
        else:
            self.api_status.setText("Sorry, wrong API key")
        
        # Show status elements
        self.status_dot.show()
        self.api_status.show()
