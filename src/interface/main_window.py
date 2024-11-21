"""
Octavia's Main Window Interface
"""

import sys
import os
import asyncio
from PySide6.QtWidgets import QMainWindow, QWidget, QHBoxLayout, QVBoxLayout, QApplication, QTextEdit
from PySide6.QtCore import Qt, QTimer
import contextlib
from PySide6.QtCore import QEventLoop
from loguru import logger

# Configure loguru to write to a file
log_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "logs", "octavia.log")
logger.add(log_path, rotation="500 MB", level="DEBUG", backtrace=True, diagnose=True)

# Add the src directory to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from interface.components import WelcomeSection, TextInput, get_global_styles, LeftPanel
from consciousness.brain.gemini_brain import GeminiBrain

class OctaviaState:
    """State management for Octavia"""
    def __init__(self):
        self.current_workspace = None
        self.active_file = None
        self.current_project = None

class MainWindow(QMainWindow):
    """Main window for Octavia"""
    def __init__(self):
        super().__init__()
        
        # Create and store event loop
        self.loop = asyncio.new_event_loop()
        asyncio.set_event_loop(self.loop)
        
        # Set up UI
        self.setWindowTitle("Octavia")
        self.resize(1200, 800)
        
        # Initialize state
        self.state = OctaviaState()
        self.brain = None
        
        # Create chat display
        self.chat_display = QTextEdit()
        self.chat_display.setReadOnly(True)
        self.chat_display.setStyleSheet("""
            QTextEdit {
                background-color: #F8EFD8;
                color: #4a4a4a;
                border: none;
                font-family: '.AppleSystemUIFont';
                font-size: 14px;
                padding: 5px 15px;
                margin: 0;
            }
            QScrollBar:vertical {
                border: none;
                background-color: transparent;
                width: 8px;
                margin: 0;
            }
            QScrollBar::handle:vertical {
                background: rgba(74, 74, 74, 0.2);
                min-height: 20px;
                border-radius: 4px;
            }
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
                height: 0;
                background: none;
            }
            QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical {
                background: none;
            }
        """)
        
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
        left_container.setFixedWidth(300)
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
        
        # Create timer for async operations
        self.async_timer = QTimer()
        self.async_timer.timeout.connect(self._process_async)
        self.async_timer.start(10)  # Run every 10ms
    
    def _process_async(self):
        """Process pending async operations"""
        self.loop.stop()
        self.loop.run_forever()
    
    def _setup_main_content(self):
        """Setup the main content area with welcome message and input"""
        right_panel = QWidget()
        layout = QVBoxLayout(right_panel)
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(8)  # Reduced spacing between elements
        
        # Add welcome section at the top
        self.welcome = WelcomeSection()
        layout.addWidget(self.welcome)
        
        # Add chat display in the middle with stretch
        layout.addWidget(self.chat_display, 1)  # Added stretch factor
        
        # Add text input at the bottom
        self.text_input = TextInput()
        self.text_input.message_sent.connect(self._handle_message)
        layout.addWidget(self.text_input)
        
        return right_panel

    def _handle_api_key(self, key: str):
        """Handle API key insertion"""
        try:
            # Initialize Gemini brain with the API key
            self.brain = GeminiBrain(api_key=key)
            
            # Enable text input and update UI
            self.text_input.setEnabled(True)
            self.text_input.setPlaceholderText("Message Octavia...")
            self.state.api_key = key  # Store the key in state
            
        except Exception as e:
            # If initialization fails, show error in API status
            self.left_panel.api_status.setText("❌ Invalid key")
            self.left_panel.api_status.show()
            self.left_panel.api_key_input.setEnabled(True)
            self.left_panel.insert_key_btn.show()

    def _handle_message(self, message: str):
        """Handle incoming message from text input."""
        # Add user message with right alignment
        user_message = f'<div style="text-align: right; margin: 8px 0;"><span style="background-color: #e8dcc8; padding: 8px 12px; border-radius: 15px; display: inline-block; max-width: 80%;">{message}</span></div>'
        self.chat_display.append(user_message)
        
        # Process message asynchronously
        asyncio.create_task(self._process_message(message))

    async def _process_message(self, message: str):
        """Process a message asynchronously"""
        print(f"\nProcessing message: {message}")
        try:
            # Get response from brain
            response = await self.brain.process_message(message)
            print(f"Received response from Gemini: {response}")
            
            # Add Octavia's response with left alignment
            octavia_message = f'<div style="text-align: left; margin: 8px 0;"><span style="background-color: #d4c3a3; padding: 8px 12px; border-radius: 15px; display: inline-block; max-width: 80%;">{response}</span></div>'
            self.chat_display.append(octavia_message)
            
            print("Message processing complete")
        except Exception as e:
            print(f"Error processing message: {e}")
            error_message = f'<div style="text-align: left; margin: 8px 0; color: #ff4444;">Error: {str(e)}</div>'
            self.chat_display.append(error_message)


def main():
    app = QApplication(sys.argv)
    
    window = MainWindow()
    window.show()
    
    try:
        sys.exit(app.exec())
    finally:
        window.loop.close()

if __name__ == "__main__":
    main()
