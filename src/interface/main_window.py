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
from consciousness.awareness.ui_abilities import UIAbilitiesRegistrarNew as UIAbilitiesRegistrar

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
        
        # Initialize UI abilities registrar
        self.abilities_registrar = UIAbilitiesRegistrar(self.ui_awareness)
        
        # Initialize UI observer
        self._initialize_ui_observer()
        
        # Connect UI observer to awareness system
        self.ui_observer.interaction_detected.connect(self._handle_ui_interaction)
        
        # Set up UI
        self.setWindowTitle("Octavia")
        self.resize(1200, 800)
        logger.debug("Window configuration set")
        
        # Initialize state
        self.state = OctaviaState()
        self.brain = None
        logger.debug("State initialized")
        
        # For typewriter effect
        self.typewriter_timer = QTimer(self)
        self.typewriter_timer.setInterval(5)
        self.typewriter_timer.timeout.connect(self._typewriter_update)
        self.current_response = ""
        self.displayed_chars = 0
        self._current_bubble = None
        self.chars_per_update = 10
        self.skip_typewriter_threshold = 50
        logger.debug("Typewriter effect configured")
        
        # Apply styles from external stylesheet
        self.setStyleSheet(get_global_styles())
        
        # Setup UI components
        self._setup_ui()
        
        # Set initial focus to text input
        QTimer.singleShot(100, lambda: self.text_input.text_input.setFocus())
        
    async def initialize(self):
        """Async initialization of components"""
        logger.info("Running async initialization...")
        try:
            # Register UI abilities
            self.abilities_registrar.register_default_abilities()  # Changed to use sync method
            
            # Initialize brain without API key
            self.brain = GeminiBrain()
            # Don't initialize brain yet - wait for API key
            
            logger.info("Async initialization complete")
            
        except Exception as e:
            logger.error(f"Error during async initialization: {str(e)}")
            raise

    def _initialize_ui_observer(self):
        """Initialize UI observer"""
        try:
            self.ui_observer = UIObserver(QApplication.instance(), self.ui_awareness, self)
            self.installEventFilter(self.ui_observer)
            logger.info("UI observer initialized")
        except Exception as e:
            logger.error(f"Error initializing UI observer: {e}")
            raise

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

    async def _on_api_key_inserted(self, api_key: str):
        """Handle API key insertion"""
        try:
            # Show loading state
            self.left_panel.set_loading_state(True)
            
            # Create brain if not exists
            if not self.brain:
                self.brain = GeminiBrain(api_key)
            else:
                self.brain.model_manager.api_key = api_key
                
            # Initialize brain
            await self.brain.initialize()
            
            logger.info("API key validated successfully")
            self.left_panel.show_success_message("API key validated!")
            
            # Enable text input after successful validation
            self.text_input.setEnabled(True)
            self.text_input.setPlaceholderText("Ask anything - use '@' to mention folder or directory blocks")
            
        except Exception as e:
            logger.error(f"Error validating API key: {e}")
            self.left_panel.show_error_message(f"Invalid API key")
            self.text_input.setEnabled(False)
            
        finally:
            self.left_panel.set_loading_state(False)

    def _handle_message(self, message: str):
        """Handle incoming message from text input."""
        try:
            # Set processing state immediately
            self.text_input.set_processing_state(True)
            
            # Create and start task
            task = asyncio.create_task(self._process_message(message))
            task.add_done_callback(lambda _: self.text_input.set_processing_state(False))
            
        except Exception as e:
            logger.error(f"Error in _handle_message: {str(e)}")
            self.chat_display.add_message(f"Error processing message: {str(e)}", is_user=False)
            self.text_input.set_processing_state(False)

    async def _process_message(self, message: str):
        """Process a message asynchronously"""
        logger.info(f"Processing message: {message}...")
        
        try:
            # Create new message bubble for Octavia's response
            self._current_bubble = self.chat_display.add_message("", is_user=False)
            
            logger.debug("Generating response...")
            # Generate response with streaming
            response_chunks = []
            self.current_response = ""
            self.displayed_chars = 0
            self.typewriter_timer.start()
            
            async for chunk in self.brain.generate_stream(message):
                response_chunks.append(chunk)
                self.current_response = "".join(response_chunks)
                # Let the typewriter effect catch up
                await asyncio.sleep(0.01)
            
            logger.info("Response generated successfully")
            
        except Exception as e:
            logger.error(f"Error processing message: {str(e)}")
            # Show error in chat
            self.chat_display.append_system_message(f"Error: {str(e)}")
            # Reset text input state
            self.text_input.set_processing_state(False)

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
            # Add stop message to conversation
            asyncio.create_task(self._handle_stop_message())
            
    async def _handle_stop_message(self):
        """Generate a contextual stop message through the brain"""
        try:
            message = "The user has requested to stop. How should I acknowledge this?"
            async for chunk in self.brain.generate_stream(message):
                self.chat_display.update_last_message(chunk)
        except Exception as e:
            logger.error(f"Error generating stop message: {e}")
            self.chat_display.add_message("I noticed you wanted me to stop. Feel free to ask me something else!", is_user=False)

    def _typewriter_update(self):
        """Update typewriter effect display"""
        if not self._current_bubble or not self.current_response:
            self.typewriter_timer.stop()
            return

        # Skip typewriter for short responses
        if len(self.current_response) <= self.skip_typewriter_threshold:
            self._current_bubble.update_text(self.current_response)
            self.typewriter_timer.stop()
            self.displayed_chars = len(self.current_response)
            return

        # Calculate chunk to display
        end_pos = min(self.displayed_chars + self.chars_per_update, len(self.current_response))
        current_text = self.current_response[:end_pos]
        
        # Update display
        self._current_bubble.update_text(current_text)
        self.displayed_chars = end_pos
        
        # Stop timer when done
        if self.displayed_chars >= len(self.current_response):
            self.typewriter_timer.stop()
            self._current_bubble.finish()
            self._current_bubble = None

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
            
    def _setup_ui(self):
        """Setup the main content area with welcome message and input"""
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
        # Connect API key signal to async slot using qasync
        self.left_panel.api_key_inserted.connect(lambda key: asyncio.create_task(self._on_api_key_inserted(key)))
        left_layout.addWidget(self.left_panel)
        main_layout.addWidget(left_container)
        
        # Create main content area
        self.right_panel = QWidget()
        layout = QVBoxLayout(self.right_panel)
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
        self.text_input = TextInput(self)
        self.text_input.message_sent.connect(self._handle_message)  # Use message_sent instead of message_submitted
        self.text_input.stop_requested.connect(self._handle_stop)
        input_layout.addWidget(self.text_input, 1)  # Add stretch factor
        
        # Add input container to main layout
        layout.addWidget(input_container)
        
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
        await window.initialize()
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
