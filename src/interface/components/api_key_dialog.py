"""
API Key Dialog Component
"""

from PySide6.QtWidgets import (QDialog, QVBoxLayout, QLabel, 
                             QLineEdit, QPushButton, QMessageBox)
from PySide6.QtCore import Qt
from loguru import logger

class APIKeyDialog(QDialog):
    """Dialog for entering Gemini API key"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Enter Gemini API Key")
        self.setModal(True)
        self.resize(400, 150)
        
        # Create layout
        layout = QVBoxLayout()
        
        # Add instructions
        instructions = QLabel(
            "Please enter your Gemini API key. You can get one from:\n"
            "https://makersuite.google.com/app/apikey"
        )
        instructions.setWordWrap(True)
        layout.addWidget(instructions)
        
        # Add API key input
        self.api_key_input = QLineEdit()
        self.api_key_input.setPlaceholderText("Enter your API key here")
        self.api_key_input.setEchoMode(QLineEdit.Password)
        layout.addWidget(self.api_key_input)
        
        # Add buttons
        button_layout = QVBoxLayout()
        
        self.submit_button = QPushButton("Submit")
        self.submit_button.clicked.connect(self.accept)
        button_layout.addWidget(self.submit_button)
        
        layout.addLayout(button_layout)
        self.setLayout(layout)
    
    def get_api_key(self):
        """Return the entered API key"""
        return self.api_key_input.text().strip()
