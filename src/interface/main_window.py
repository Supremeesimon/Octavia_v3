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
from interface.awareness.ui_observer import UIObserver
from interface.awareness.ui_awareness import UIAwarenessSystem
from consciousness.awareness.ui_abilities import UIAbilitiesRegistrar

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
        
        # Initialize UI awareness systems
        self.ui_awareness = UIAwarenessSystem()
        self.ui_observer = UIObserver(self)
        self.installEventFilter(self.ui_observer)  # Install event filter
        
        # Connect UI observer to awareness system
        self.ui_observer.interaction_detected.connect(self._handle_ui_interaction)
        
        # Set up UI
        self.setWindowTitle("Octavia")
        self.resize(1200, 800)
        logger.debug("Window configuration set")
        
        # Initialize state
        self.state = OctaviaState()
        self.brain = GeminiBrain()  # Initialize without API key
        logger.debug("State initialized")
        
        # For typewriter effect
        self.typewriter_timer = QTimer(self)  # Ensure timer has parent
        self.typewriter_timer.setInterval(20)  # 20ms between updates (slower)
        self.typewriter_timer.timeout.connect(self._typewriter_update)
        self.current_response = ""
        self.displayed_chars = 0
        self._current_bubble = None  # Initialize bubble reference
        self.chars_per_update = 3  # Reduced from 10 to 3 chars per update
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
        
        # Use qasync's event loop
        self.loop = asyncio.get_event_loop()
        
        # Create timer for async operations
        self.async_timer = QTimer()
        self.async_timer.timeout.connect(self._process_async)
        self.async_timer.start(1)  # Run every 1ms
        
        # Queue for async tasks
        self.task_queue = []
        
        # Initialize UI abilities after brain is ready
        self.ui_abilities = None
        
    def _process_async(self):
        """Process pending async operations"""
        try:
            # Process up to 5 tasks at once
            for _ in range(min(5, len(self.task_queue))):
                if self.task_queue:
                    task = self.task_queue.pop(0)
                    asyncio.create_task(task)
        except Exception as e:
            logger.error(f"Error in _process_async: {str(e)}")
            import traceback
            logger.error(traceback.format_exc())

    def _on_api_key_inserted(self, key: str):
        """Handle API key insertion by scheduling async validation"""
        logger.info("API key inserted - scheduling validation...")
        try:
            # Update UI to show validation in progress
            self.text_input.setEnabled(False)
            self.text_input.setPlaceholderText("Validating API key...")
            
            # Schedule async validation
            asyncio.create_task(self._handle_api_key(key))
            
        except Exception as e:
            logger.error(f"Error scheduling API key validation: {str(e)}")
            self.text_input.setEnabled(False)
            self.text_input.setPlaceholderText("Error validating key - please try again")
            self.left_panel.set_api_error("Error validating key")

    async def _handle_api_key(self, key: str):
        """Handle API key validation"""
        logger.info("Attempting API key validation...")
        try:
            # Initialize model with key first
            self.brain.model_manager._initialize_model(key)
            
            # Test the API key with a simple query
            if await self.brain.model_manager.test_connection():
                logger.info("API key validated successfully")
                self.text_input.setEnabled(True)
                self.text_input.setPlaceholderText("Type your message...")
                self.left_panel.set_api_success()
                
                # Initialize UI abilities after brain is ready
                self.ui_abilities = UIAbilitiesRegistrar(self.brain.abilities)
                await self.ui_abilities.register_ui_abilities()
                
            else:
                logger.error("API key validation failed - invalid key")
                self.text_input.setEnabled(False)
                self.text_input.setPlaceholderText("Invalid API key - please try again")
                self.left_panel.set_api_error("Invalid API key")
                
        except Exception as e:
            logger.error(f"API key validation failed with error: {str(e)}")
            self.text_input.setEnabled(False)
            self.text_input.setPlaceholderText("Connection error - please try again")
            self.left_panel.set_api_error("Connection error - please try again")
            
    def _handle_message(self, message: str):
        """Handle incoming message from text input."""
        try:
            # Add user message to chat
            self.chat_display.add_message(message, is_user=True)
            
            # Process message asynchronously
            self.task_queue.append(self._process_message(message))
            
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
                self.chat_display.add_message("Error: Please enter your API key first.", is_user=False)
                self.text_input.message_processed()
                return

            logger.debug("Generating response...")
            response = await self.brain.generate_response(message)
            if response:
                logger.info("Response generated successfully")
                # Start typewriter effect
                self.current_response = response
                self.displayed_chars = 0
                self.typewriter_timer.start()
                # Don't call message_processed() here - wait for typewriter to finish
            else:
                logger.error("No response generated")
                self.chat_display.add_message("Error: Failed to generate response.", is_user=False)
                self.text_input.message_processed()

        except Exception as e:
            logger.error(f"Error processing message: {str(e)}")
            self.chat_display.add_message(f"Error: {str(e)}", is_user=False)
            self.text_input.message_processed()

    def _handle_stop(self):
        """Handle stop request from text input"""
        logger.info("Stop requested by user")
        
        # Stop the typewriter effect first
        if self.typewriter_timer.isActive():
            self.typewriter_timer.stop()
            # Finish the current message with what we have so far
            self.chat_display.finish_message()
            
        # Request stop from brain
        if self.brain:
            self.brain.request_stop()
            
        # Reset the text input state
        self.text_input.message_processed()
        self.current_response = ""
        self.displayed_chars = 0

    def _typewriter_update(self):
        """Update typewriter effect"""
        try:
            if not self.current_response:
                logger.debug("No current response to update")
                self.typewriter_timer.stop()
                return

            if self.displayed_chars == 0:
                logger.debug("Creating new message bubble")
                # Create initial empty message
                self.chat_display.add_message("", is_user=False)

            # Calculate next chunk of text to display
            remaining = len(self.current_response) - self.displayed_chars
            next_chars = min(self.chars_per_update, remaining)
            
            if next_chars > 0:
                # Update the current message with more text
                displayed_text = self.current_response[:self.displayed_chars + next_chars]
                self.chat_display.update_last_message(displayed_text)
                self.displayed_chars += next_chars
                
                # If this is the last update, finish the message
                if self.displayed_chars >= len(self.current_response):
                    logger.debug("Typewriter effect complete")
                    self.typewriter_timer.stop()
                    self.chat_display.finish_message()
                    self.text_input.message_processed()  # Re-enable input
                    self.current_response = ""
                    self.displayed_chars = 0
            else:
                # No more characters to display
                logger.debug("No more characters to display")
                self.typewriter_timer.stop()
                self.chat_display.finish_message()
                self.text_input.message_processed()
                self.current_response = ""
                self.displayed_chars = 0
                
        except Exception as e:
            logger.error(f"Error in typewriter update: {str(e)}")
            self.typewriter_timer.stop()
            self.chat_display.finish_message()
            self.text_input.message_processed()
            
    def _handle_ui_interaction(self, context: dict):
        """Handle UI interaction events from observer"""
        try:
            # Update UI awareness system
            self.ui_awareness.update_mouse_context(context)
            
            # Get any contextual suggestions
            suggestions = self.ui_awareness.get_interaction_suggestions()
            
            # If we have relevant suggestions and brain is ready
            if suggestions and self.brain and self.brain.is_ready():
                # Add to brain's context without interrupting
                asyncio.create_task(
                    self.brain.update_interaction_context({
                        "ui_interaction": context,
                        "suggestions": suggestions
                    })
                )
                
        except Exception as e:
            logger.error(f"Error handling UI interaction: {e}")
            
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
        self.text_input.message_sent.connect(self._handle_message)  # Use message_sent instead of message_submitted
        self.text_input.stop_requested.connect(self._handle_stop)
        input_layout.addWidget(self.text_input, 1)  # Add stretch factor
        
        # Add input container to main layout
        layout.addWidget(input_container)
        
        return right_panel

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
