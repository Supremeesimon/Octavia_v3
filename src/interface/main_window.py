"""
Octavia's Main Window Interface
"""

import sys
import asyncio
from pathlib import Path
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, 
    QTextEdit, QLineEdit, QPushButton, QScrollArea
)
from PySide6.QtCore import Qt, Signal, Slot, QTimer
from qt_material import apply_stylesheet

from ..consciousness.interface.conversation_handler import ConversationHandler

class ChatWidget(QWidget):
    """Widget for chat interface"""
    
    message_sent = Signal(str)
    
    def __init__(self):
        super().__init__()
        self.init_ui()
        
    def init_ui(self):
        """Initialize the UI components"""
        layout = QVBoxLayout()
        
        # Chat history area
        self.chat_area = QTextEdit()
        self.chat_area.setReadOnly(True)
        layout.addWidget(self.chat_area)
        
        # Message input
        self.message_input = QLineEdit()
        self.message_input.setPlaceholderText("Type your message here...")
        self.message_input.returnPressed.connect(self.send_message)
        layout.addWidget(self.message_input)
        
        # Send button
        self.send_button = QPushButton("Send")
        self.send_button.clicked.connect(self.send_message)
        layout.addWidget(self.send_button)
        
        self.setLayout(layout)
        
    def send_message(self):
        """Send the message from input field"""
        message = self.message_input.text().strip()
        if message:
            self.message_sent.emit(message)
            self.message_input.clear()
            
    def append_message(self, sender: str, message: str):
        """Add a message to the chat area"""
        self.chat_area.append(f"{sender}: {message}\n")

class MainWindow(QMainWindow):
    """Main window for Octavia"""
    
    def __init__(self):
        super().__init__()
        self.init_ui()
        self.init_octavia()
        
    def init_ui(self):
        """Initialize the UI components"""
        self.setWindowTitle("Octavia v3")
        self.setMinimumSize(600, 400)
        
        # Create central widget
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        
        # Create layout
        layout = QVBoxLayout(self.central_widget)
        
        # Add chat widget
        self.chat_widget = ChatWidget()
        self.chat_widget.message_sent.connect(self.handle_message)
        layout.addWidget(self.chat_widget)
        
    def init_octavia(self):
        """Initialize Octavia's conversation handler"""
        self.conversation = ConversationHandler()
        
    async def process_message(self, message: str):
        """Process message through Octavia"""
        try:
            # Display user message
            self.chat_widget.append_message("You", message)
            
            # Get Octavia's response
            response = await self.conversation.process_message(message)
            
            # Display Octavia's response
            self.chat_widget.append_message("Octavia", response)
            
        except Exception as e:
            self.chat_widget.append_message(
                "System", 
                "I apologize, but I encountered an error processing your message."
            )
    
    @Slot(str)
    def handle_message(self, message: str):
        """Handle incoming messages"""
        asyncio.create_task(self.process_message(message))

def main():
    """Main entry point for the application"""
    app = QApplication(sys.argv)
    
    # Apply material theme
    apply_stylesheet(app, theme='dark_teal.xml')
    
    # Create and show window
    window = MainWindow()
    window.show()
    
    # Start event loop
    sys.exit(app.exec())
