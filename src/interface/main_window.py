"""
Octavia's Main Window Interface
"""

import sys
import os
from PySide6.QtWidgets import QMainWindow, QWidget, QHBoxLayout, QVBoxLayout, QApplication
from PySide6.QtCore import Qt

# Add the src directory to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from interface.components import WelcomeSection, TextInput, OctaviaState, get_global_styles, LeftPanel

class MainWindow(QMainWindow):
    """Main window for Octavia"""
    def __init__(self):
        super().__init__()
        self.state = OctaviaState()
        self.setWindowTitle("Octavia")
        self.setMinimumSize(1200, 800)
        
        # Apply styles from external stylesheet
        self.setStyleSheet(get_global_styles())
        
        # Setup main layout
        main_widget = QWidget()
        main_widget.setObjectName("mainWidget")
        main_layout = QHBoxLayout(main_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        
        # Create left sidebar container with background
        left_container = QWidget()
        left_container.setObjectName("leftContainer")
        left_container.setStyleSheet("QWidget#leftContainer { background-color: #e8dcc8; border-top-right-radius: 10px; border-bottom-right-radius: 10px; }")
        left_layout = QHBoxLayout(left_container)
        left_layout.setContentsMargins(0, 0, 0, 0)
        left_layout.setSpacing(0)
        
        # Create left sidebar
        self.left_panel = LeftPanel()
        self.left_panel.api_key_inserted.connect(self._handle_api_key)
        left_layout.addWidget(self.left_panel)
        main_layout.addWidget(left_container)
        
        # Create main content area
        self.right_panel = self._setup_main_content()
        main_layout.addWidget(self.right_panel)
        
        self.setCentralWidget(main_widget)
        
        # Initialize with text input disabled
        self.text_input.setEnabled(False)
        self.text_input.setPlaceholderText("Enter activation key to start...")

    def _setup_main_content(self):
        """Setup the main content area with welcome message and input"""
        right_panel = QWidget()
        layout = QVBoxLayout(right_panel)
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(20)

        # Container for both welcome and input
        content_container = QWidget()
        content_layout = QVBoxLayout(content_container)
        content_layout.setContentsMargins(0, 0, 0, 0)
        content_layout.setSpacing(20)

        # Welcome section
        welcome = WelcomeSection()
        welcome.setFixedWidth(850)  # Match text input width
        content_layout.addWidget(welcome)
        
        # Text input
        self.text_input = TextInput()
        self.text_input.message_sent.connect(self._handle_message)
        content_layout.addWidget(self.text_input)
        
        # Center the content container
        container_wrapper = QHBoxLayout()
        container_wrapper.addStretch()
        container_wrapper.addWidget(content_container)
        container_wrapper.addStretch()
        
        layout.addLayout(container_wrapper)
        layout.addStretch()
        
        return right_panel

    def _handle_api_key(self, key: str):
        """Handle API key insertion"""
        # Here you would validate the key with Gemini
        # For now, we'll just enable the text input
        self.text_input.setEnabled(True)
        self.text_input.setPlaceholderText("Message Octavia...")
        self.state.api_key = key  # Store the key in state

    def _handle_message(self, message: str):
        """Handle messages sent from the text input"""
        print(f"Message received: {message}")  # For now, just print the message


def main():
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
