"""
Octavia's Main Window Interface
"""

import sys
import os
import asyncio
import qasync
from PySide6.QtWidgets import QMainWindow, QWidget, QHBoxLayout, QVBoxLayout, QApplication, QTextEdit
from PySide6.QtCore import Qt, QTimer
from PySide6.QtGui import QTextCursor
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
        
        # Set up UI
        self.setWindowTitle("Octavia")
        self.resize(1200, 800)
        
        # Initialize state
        self.state = OctaviaState()
        self.brain = None
        
        # For typewriter effect
        self.typewriter_timer = QTimer()
        self.typewriter_timer.setInterval(10)  # 10ms between characters (very fast)
        self.typewriter_timer.timeout.connect(self._typewriter_update)
        self.current_response = ""
        self.displayed_chars = 0
        
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
        self.left_panel.api_key_inserted.connect(self._on_api_key_inserted)
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
        try:
            loop = asyncio.get_event_loop()
            if loop.is_running():
                return
            loop.call_soon(loop.stop)
            loop.run_forever()
        except Exception as e:
            print(f"Error in _process_async: {str(e)}")
            import traceback
            print(traceback.format_exc())

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
        layout.addWidget(self.chat_display, 1)  # Added stretch factor
        
        # Create a container for the text input to handle stretching
        input_container = QWidget()
        input_layout = QHBoxLayout(input_container)
        input_layout.setContentsMargins(0, 0, 0, 0)
        input_layout.setSpacing(0)
        
        # Add text input with stretch
        self.text_input = TextInput()
        self.text_input.message_sent.connect(self._handle_message)
        input_layout.addWidget(self.text_input, 1)  # Add stretch factor
        
        # Add input container to main layout
        layout.addWidget(input_container)
        
        return right_panel

    def _on_api_key_inserted(self, key: str):
        """Handle API key insertion by scheduling async validation"""
        loop = asyncio.get_event_loop()
        loop.create_task(self._handle_api_key(key))

    async def _handle_api_key(self, key: str):
        """Handle API key validation"""
        try:
            # Initialize brain with API key
            self.brain = GeminiBrain(key)
            # Test the API key
            is_valid = await self.brain.test_api_key()
            
            if is_valid:
                self.left_panel.set_api_success()
                self.text_input.setEnabled(True)
                self.text_input.setPlaceholderText("Type your message...")
                self.text_input.setFocus()
            else:
                error_msg = "Invalid API key - Please check your key and try again"
                self.left_panel.set_api_error(error_msg)
                self.brain = None
        except Exception as e:
            logger.error(f"API key validation error: {str(e)}")
            self.left_panel.set_api_error(f"Error: {str(e)}")
            self.brain = None

    def _handle_message(self, message: str):
        """Handle incoming message from text input."""
        try:
            # Add user message with right alignment in right 60% of space
            user_message = f'''
                <table width="100%" cellspacing="0" cellpadding="0">
                    <tr>
                        <td width="40%"></td>
                        <td width="60%" align="right">
                            <div style="
                                padding: 12px 16px; 
                                border-radius: 20px;
                                display: inline-block;
                                max-width: 100%;
                                word-wrap: break-word;
                                margin: 4px 0;
                            ">{message}</div>
                        </td>
                    </tr>
                </table>
            '''
            self.chat_display.append(user_message)
            
            # Process message asynchronously
            loop = asyncio.get_event_loop()
            loop.create_task(self._process_message(message))
            
        except Exception as e:
            print(f"Error in _handle_message: {str(e)}")
            import traceback
            print(traceback.format_exc())

    async def _process_message(self, message: str):
        """Process a message asynchronously"""
        try:
            # Get response from brain
            response = await self.brain.process_message(message)
            
            # Prepare for typewriter effect
            self.current_response = response
            self.displayed_chars = 0
            
            # Add Octavia's response container
            octavia_container = f'''
                <table width="100%" cellspacing="0" cellpadding="0">
                    <tr>
                        <td width="60%">
                            <div style="
                                padding: 12px 16px; 
                                border-radius: 20px;
                                display: inline-block;
                                max-width: 100%;
                                word-wrap: break-word;
                                margin: 4px 0;
                            "></div>
                        </td>
                        <td width="40%"></td>
                    </tr>
                </table>
            '''
            self.chat_display.append(octavia_container)
            
            # Start typewriter effect
            self.typewriter_timer.start()
            
        except Exception as e:
            error_message = f'''
                <table width="100%" cellspacing="0" cellpadding="0">
                    <tr>
                        <td width="60%">
                            <div style="
                                color: #ff4444;
                                padding: 12px 16px; 
                                border-radius: 20px;
                                display: inline-block;
                                max-width: 100%;
                                word-wrap: break-word;
                                margin: 4px 0;
                            ">{str(e)}</div>
                        </td>
                        <td width="40%"></td>
                    </tr>
                </table>
            '''
            self.chat_display.append(error_message)
            # Re-enable text input on error
            self.text_input.message_processed()

    def _typewriter_update(self):
        """Update typewriter effect"""
        if self.displayed_chars < len(self.current_response):
            # Get next chunk of characters (3 chars at a time for speed)
            chunk_size = 3
            next_chars = self.current_response[self.displayed_chars:self.displayed_chars + chunk_size]
            self.displayed_chars += chunk_size
            
            # Add the next characters
            cursor = self.chat_display.textCursor()
            cursor.movePosition(QTextCursor.End)
            cursor.insertText(next_chars)
            self.chat_display.setTextCursor(cursor)
            
            # Scroll to bottom
            self.chat_display.verticalScrollBar().setValue(
                self.chat_display.verticalScrollBar().maximum()
            )
        else:
            self.typewriter_timer.stop()
            # Re-enable text input
            self.text_input.message_processed()


async def main():
    """Main entry point for Octavia"""
    app = QApplication.instance()
    if not app:
        app = QApplication(sys.argv)
    
    try:
        loop = qasync.QEventLoop(app)
        asyncio.set_event_loop(loop)
        
        window = MainWindow()
        window.show()
        
        with loop:
            loop.run_forever()
    except Exception as e:
        print(f"Error in main: {str(e)}")
        import traceback
        print(traceback.format_exc())

if __name__ == "__main__":
    asyncio.run(main())
