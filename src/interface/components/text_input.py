"""
Text input component for Octavia
"""

from PySide6.QtWidgets import (QWidget, QHBoxLayout, QTextEdit, QPushButton,
                              QVBoxLayout, QLabel)
from PySide6.QtCore import Signal, Qt, QTimer, QEvent, Property
from .toggle_switch import ToggleSwitch
from loguru import logger

class TextInput(QWidget):
    message_sent = Signal(str)
    mode_changed = Signal(bool)
    stop_requested = Signal()

    def __init__(self, main_window, parent=None):
        super().__init__(parent)
        self.main_window = main_window  # Store reference to main window
        self.action_mode = False  # Set chat mode as default
        self.setup_ui()
        self.setup_connections()
        self._enabled = True
        self._is_sending = False

    def setup_ui(self):
        self.setObjectName("inputGroup")
        # Remove fixed width to allow stretching
        self.setMinimumWidth(850)  
        self.setMinimumHeight(48)
        
        # Main vertical layout to control expansion direction
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # Add stretch to push content to bottom
        main_layout.addStretch()
        
        # Content widget that will expand
        self.input_container = QWidget()
        input_layout = QHBoxLayout(self.input_container)
        input_layout.setContentsMargins(8, 4, 8, 4)
        input_layout.setSpacing(4)

        # Text input
        self.text_input = QTextEdit()
        self.text_input.setObjectName("textInput")
        self.text_input.setPlaceholderText("Ask anything - use '@' to mention folder or file")
        self.text_input.setFixedHeight(36)
        self.text_input.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        input_layout.addWidget(self.text_input, 1)

        # Right side controls
        self.right_container = QWidget()
        self.right_container.setObjectName("rightContainer")
        self.right_container.setFixedWidth(80)  
        right_layout = QHBoxLayout(self.right_container)
        right_layout.setContentsMargins(0, 0, 0, 0)
        right_layout.setSpacing(12)  

        # Attachment button
        self.attach_button = QPushButton("📎")
        self.attach_button.setObjectName("attachButton")
        self.attach_button.setFixedSize(32, 32)
        self.attach_button.setToolTip("Attach files (images, PDFs, documents)")
        right_layout.addWidget(self.attach_button)

        # Send/Stop button
        self.send_button = QPushButton("→")  
        self.send_button.setObjectName("sendButton")
        self.send_button.setFixedSize(32, 32)  
        self.send_button.setToolTip("Send message")
        # Match text input background color
        self.send_button.setStyleSheet("""
            QPushButton#sendButton {
                border: 1px solid #e8dcc8;
                border-radius: 16px;
                background: #eadfd0;
                color: #8B7355;
                font-size: 20px;
            }
            QPushButton#sendButton[stop="true"] {
                background: #d4c5b3;
                color: #6b563f;
                font-size: 14px;
                font-weight: bold;
            }
            QPushButton#sendButton:hover {
                background: #e8dcc8;
                color: #8B7355;
            }
            QPushButton#sendButton[stop="true"]:hover {
                background: #c4b5a3;
                color: #5b462f;
            }
        """)
        right_layout.addWidget(self.send_button)

        # Loading dots for send button (hidden by default)
        self._loading_timer = QTimer()
        self._loading_timer.setInterval(500)  # Update every 500ms
        self._loading_timer.timeout.connect(self._update_loading_dots)
        self._loading_dots = 0

        input_layout.addWidget(self.right_container)
        main_layout.addWidget(self.input_container)

        # Mode toggle below input
        self.mode_container = QWidget()
        self.mode_container.setObjectName("modeContainer")
        self.mode_container.setFixedWidth(190)  
        mode_layout = QHBoxLayout(self.mode_container)
        mode_layout.setContentsMargins(0, 0, 0, 0)
        mode_layout.setSpacing(8)  

        # Action mode label
        self.action_label = QLabel("Action mode")
        self.action_label.setObjectName("modeLabel")
        self.action_label.setFixedWidth(75)  
        mode_layout.addWidget(self.action_label)

        # Toggle switch
        self.mode_toggle = ToggleSwitch()
        self.mode_toggle.setChecked(True)  # Set to Chat mode by default
        mode_layout.addWidget(self.mode_toggle)

        # Chat mode label
        self.chat_label = QLabel("Chat mode")
        self.chat_label.setObjectName("modeLabel")
        self.chat_label.setFixedWidth(75)  
        mode_layout.addWidget(self.chat_label)

        # Add mode toggle below input with right alignment
        mode_wrapper = QHBoxLayout()
        mode_wrapper.addStretch()
        mode_wrapper.addWidget(self.mode_container)
        mode_wrapper.setContentsMargins(0, 0, 8, 0)
        main_layout.addLayout(mode_wrapper)

    def setup_connections(self):
        self.send_button.clicked.connect(self._send_message)
        self.text_input.textChanged.connect(self._adjust_height)
        self.mode_toggle.toggled.connect(self._handle_mode_toggle)
        
        # Handle key events in text input
        self.text_input.installEventFilter(self)

    def eventFilter(self, obj, event):
        """Handle key events in text input"""
        if obj == self.text_input and event.type() == QEvent.KeyPress:
            if event.key() == Qt.Key_Return or event.key() == Qt.Key_Enter:
                # Send message on Enter without Shift
                if not event.modifiers() & Qt.ShiftModifier:
                    self._on_return_pressed()
                    return True
                # Allow Shift+Enter for new line
                return False
        return super().eventFilter(obj, event)

    def _on_return_pressed(self):
        """Handle return key press"""
        try:
            # Get message
            message = self.text_input.toPlainText().strip()
            if not message:
                return
                
            # Clear input immediately
            self.text_input.clear()
            self.text_input.setPlainText("")
            
            # Add message to chat display immediately
            self.main_window.chat_display.add_message(message, is_user=True)
            
            # Emit message signal for processing
            self.message_sent.emit(message)
            
            # Set processing state
            self.set_processing_state(True)
            
            # Keep focus on text input
            self.text_input.setFocus()
            
            # Scroll chat to bottom
            QTimer.singleShot(50, self.main_window.chat_display._ensure_scrolled_to_bottom)
            
        except Exception as e:
            logger.error(f"Error in text input: {str(e)}")
            self.main_window.chat_display.append_system_message(f"Error: {str(e)}")

    def _send_message(self):
        """Legacy method - kept for compatibility"""
        self._on_return_pressed()

    def message_processed(self):
        """Call this when the message has been processed"""
        self._is_sending = False
        self.text_input.setEnabled(True)
        self.send_button.setText("→")
        self.send_button.setProperty("stop", False)
        self.send_button.style().unpolish(self.send_button)
        self.send_button.style().polish(self.send_button)
        self.send_button.setToolTip("Send message")
        # Set focus back to text input
        self.text_input.setFocus()

    def _update_loading_dots(self):
        """Update loading animation dots"""
        if not self._is_sending:
            self._loading_timer.stop()
            self.send_button.setText("→")
            return
            
        self._loading_dots = (self._loading_dots + 1) % 3
        dots = "•" * (self._loading_dots + 1)
        self.send_button.setText(dots)

    def _adjust_height(self):
        document_height = self.text_input.document().size().height()
        if document_height <= 36:  # Single line height
            self.text_input.setFixedHeight(36)
        else:
            max_height = min(document_height + 12, 120)  # Add padding, cap at 120px
            self.text_input.setFixedHeight(int(max_height))

    def _reset_height(self):
        self.text_input.setFixedHeight(36)

    def _handle_mode_toggle(self, checked):
        self.action_mode = not checked
        self.mode_changed.emit(checked)

    def setEnabled(self, enabled):
        self._enabled = enabled
        self.text_input.setEnabled(enabled)
        self.attach_button.setEnabled(enabled)
        self.send_button.setEnabled(enabled)
        self.mode_toggle.setEnabled(enabled)

    def setPlaceholderText(self, text):
        self.text_input.setPlaceholderText(text)

    def clear(self):
        """Clear the text input"""
        self.text_input.clear()
        
    def text(self):
        """Get the current text"""
        return self.text_input.toPlainText()
        
    def setText(self, text):
        """Set the text input content"""
        self.text_input.setPlainText(text)

    def set_processing_state(self, is_processing: bool):
        """Set the processing state of the input"""
        self._is_sending = is_processing
        self.text_input.setEnabled(not is_processing)
        
        # Update button appearance and function
        if is_processing:
            self.send_button.setText("⬛")  # Stop square
            self.send_button.setProperty("stop", True)
            self.send_button.setToolTip("Stop Octavia")
            self.send_button.clicked.disconnect()
            self.send_button.clicked.connect(self._stop_generation)
        else:
            self.send_button.setText("→")
            self.send_button.setProperty("stop", False)
            self.send_button.setToolTip("Send message")
            self.send_button.clicked.disconnect()
            self.send_button.clicked.connect(self._send_message)
            
        # Update button style
        self.send_button.style().unpolish(self.send_button)
        self.send_button.style().polish(self.send_button)
        
    def _stop_generation(self):
        """Handle stop button click"""
        self.stop_requested.emit()
        # Let main window handle the stop through brain
        self.main_window.handle_stop()
        self.set_processing_state(False)

    def is_processing(self) -> bool:
        """Return whether input is in processing state"""
        return self._is_sending
