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
        status_layout.setSpacing(8)
        
        self.status_dot = PulsingDot(self)
        status_layout.addWidget(self.status_dot)
        
        self.api_status = QLabel("")
        self.api_status.setObjectName("apiKeyStatus")
        self.api_status.setAttribute(Qt.WA_TranslucentBackground)  # Make background transparent
        status_layout.addWidget(self.api_status)
        
        status_layout.addStretch()  # Push dot and text to the left
        layout.addLayout(status_layout)
        
        # Initially hide status
        self.api_status.hide()
        self.status_dot.hide()
        
    def _handle_key_insert(self):
        """Handle API key insertion"""
        key = self.api_key_input.text().strip()
        if key:
            # Just emit the key, don't change UI state yet
            self.api_key_inserted.emit(key)
            
    def set_api_success(self):
        """Handle successful API key validation"""
        self.api_key_input.clear()
        self.api_key_input.setEnabled(False)
        self.insert_key_btn.hide()
        
        # Update status dot
        self.status_dot.set_success()
        self.status_dot.show()
        
        # Update status text
        self.api_status.setStyleSheet("color: #2ecc71; background: transparent;")  # Green color with transparent background
        self.api_status.setText("✓ API key activated")
        self.api_status.show()
        
    def set_api_error(self, error_msg=None):
        """Handle failed API key validation"""
        self.api_key_input.clear()
        self.api_key_input.setEnabled(True)
        self.api_key_input.setFocus()
        self.insert_key_btn.show()
        
        # Update status dot
        self.status_dot.set_error()
        self.status_dot.show()
        
        # Update status text
        self.api_status.setStyleSheet("color: #e74c3c; background: transparent;")  # Red color with transparent background
        self.api_status.setText(error_msg if error_msg else "Invalid API key")
        self.api_status.show()
