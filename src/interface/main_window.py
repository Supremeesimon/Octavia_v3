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
log_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "logs")
os.makedirs(log_dir, exist_ok=True)
log_path = os.path.join(log_dir, "octavia.log")
logger.add(log_path, rotation="500 MB", level="DEBUG", backtrace=True, diagnose=True,
           format="<green>{time:YYYY-MM-DD HH:mm:ss.SSS}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>")

logger.info("Starting Octavia initialization...")

# Add the src directory to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from interface.components import WelcomeSection, TextInput, get_global_styles, LeftPanel, ChatDisplay
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
        logger.info("Initializing MainWindow...")
        
        # Set up UI
        self.setWindowTitle("Octavia")
        self.resize(1200, 800)
        logger.debug("Window configuration set")
        
        # Initialize state
        self.state = OctaviaState()
        self.brain = None
        logger.debug("State initialized")
        
        # For typewriter effect
        self.typewriter_timer = QTimer(self)  # Ensure timer has parent
        self.typewriter_timer.setInterval(50)  # 50ms between updates (slower)
        self.typewriter_timer.timeout.connect(self._typewriter_update)
        self.current_response = ""
        self.displayed_chars = 0
        self._current_bubble = None  # Initialize bubble reference
        logger.debug("Typewriter effect configured")
        
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
        self.chat_display = ChatDisplay()
        layout.addWidget(self.chat_display, 1)  # Added stretch factor
        
        # Create a container for the text input to handle stretching
        input_container = QWidget()
        input_layout = QHBoxLayout(input_container)
        input_layout.setContentsMargins(0, 0, 0, 0)
        input_layout.setSpacing(0)
        
        # Add text input with stretch
        self.text_input = TextInput()
        self.text_input.message_sent.connect(self._handle_message)
        self.text_input.stop_requested.connect(self._handle_stop)
        input_layout.addWidget(self.text_input, 1)  # Add stretch factor
        
        # Add input container to main layout
        layout.addWidget(input_container)
        
        return right_panel

    def _on_api_key_inserted(self, key: str):
        """Handle API key insertion by scheduling async validation"""
        logger.info("API key inserted - scheduling validation...")
        loop = asyncio.get_event_loop()
        loop.create_task(self._handle_api_key(key))

    async def _handle_api_key(self, key: str):
        """Handle API key validation"""
        logger.info("Attempting API key validation...")
        try:
            # Initialize brain with the API key
            self.brain = GeminiBrain(key)
            logger.debug("Brain initialized with API key")
            
            # Test the API key with a simple query
            test_response = await self.brain.test_connection()
            if test_response:
                logger.info("API key validated successfully")
                self.text_input.setEnabled(True)
                self.text_input.setPlaceholderText("Type your message...")
                self.left_panel.set_api_success()  # Update left panel status only
            else:
                logger.error("API key validation failed - no response from test")
                self.left_panel.set_api_error("Invalid API key")  # Update left panel status
                self.brain = None
                
        except Exception as e:
            logger.error(f"API key validation failed with error: {str(e)}")
            self.left_panel.set_api_error(str(e))  # Update left panel status
            self.brain = None

    def _handle_message(self, message: str):
        """Handle incoming message from text input."""
        try:
            # Add user message to chat
            self.chat_display.add_message(message, is_user=True)
            
            # Process message asynchronously
            asyncio.create_task(self._process_message(message))
            
        except Exception as e:
            logger.error(f"Error in _handle_message: {str(e)}")
            self.chat_display.add_message(f"Error processing message: {str(e)}", is_user=False)
            self.text_input.message_processed()

    async def _process_message(self, message: str):
        """Process a message asynchronously"""
        logger.info(f"Processing message: {message[:50]}...")  # Log first 50 chars of message
        try:
            if not self.brain:
                logger.error("Brain not initialized - cannot process message")
                self.chat_display.add_message("System not ready. Please enter API key first.", is_user=False)
                self.text_input.message_processed()  # Re-enable input
                return

            # Start response generation
            logger.debug("Generating response...")
            response = await self.brain.generate_response(message)
            
            if response:
                logger.info("Response generated successfully")
                # Start typewriter effect
                self.current_response = response
                self.displayed_chars = 0
                self._current_bubble = None  # Reset bubble reference
                self.typewriter_timer.start()  # Start the timer
            else:
                logger.error("No response generated")
                self.chat_display.add_message("I apologize, but I couldn't generate a proper response at this time.", is_user=False)
                self.text_input.message_processed()

        except Exception as e:
            logger.error(f"Error processing message: {str(e)}")
            self.chat_display.add_message(f"I encountered an error: {str(e)}", is_user=False)
            self.text_input.message_processed()  # Re-enable input on error

    def _handle_stop(self):
        """Handle stop request from text input"""
        if self.typewriter_timer.isActive():
            self.typewriter_timer.stop()
            self.chat_display.finish_message()
            self.text_input.message_processed()

    def _typewriter_update(self):
        """Update typewriter effect"""
        try:
            if not hasattr(self, 'current_response') or not self.current_response:
                logger.error("No response to display")
                self.typewriter_timer.stop()
                return

            if self.displayed_chars < len(self.current_response):
                # Get next chunk of characters
                chunk_size = 3  # Display 3 characters at a time
                next_chars = self.current_response[self.displayed_chars:self.displayed_chars + chunk_size]
                self.displayed_chars += chunk_size
                
                # Update the current message or create new one
                if not self._current_bubble:
                    logger.debug("Creating new message bubble")
                    self._current_bubble = self.chat_display.add_message(next_chars, is_user=False)
                else:
                    logger.debug("Updating existing message bubble")
                    self._current_bubble.update_text(self.current_response[:self.displayed_chars])
                
                # Ensure we scroll to see new content
                self.chat_display._ensure_scrolled_to_bottom()
            else:
                logger.debug("Typewriter effect complete")
                self.typewriter_timer.stop()
                self._current_bubble = None
                self.text_input.message_processed()

        except Exception as e:
            logger.error(f"Error in typewriter update: {str(e)}")
            self.typewriter_timer.stop()
            self._current_bubble = None
            self.text_input.message_processed()


async def main():
    """Main entry point for Octavia"""
    logger.info("Starting main application...")
    app = QApplication.instance()
    if not app:
        app = QApplication(sys.argv)
        logger.debug("Created new QApplication instance")
    
    try:
        loop = qasync.QEventLoop(app)
        asyncio.set_event_loop(loop)
        logger.debug("Event loop initialized")
        
        window = MainWindow()
        window.show()
        logger.info("Main window created and displayed")
        
        with loop:
            logger.info("Entering main event loop")
            loop.run_forever()
    except Exception as e:
        logger.critical(f"Critical error in main: {str(e)}")
        import traceback
        logger.critical(traceback.format_exc())
        print(f"Error in main: {str(e)}")
        print(traceback.format_exc())

if __name__ == "__main__":
    asyncio.run(main())
