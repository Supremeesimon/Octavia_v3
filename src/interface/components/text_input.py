"""
Text input component for Octavia
"""

from PySide6.QtWidgets import (QWidget, QHBoxLayout, QTextEdit, QPushButton,
                              QVBoxLayout, QLabel)
from PySide6.QtCore import Signal, Qt, QTimer, QEvent, Property
from .toggle_switch import ToggleSwitch


class TextInput(QWidget):
    message_sent = Signal(str)
    mode_changed = Signal(bool)
    stop_requested = Signal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.action_mode = True
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
                background: #eadfd0;
                color: #8B7355;
                font-family: Arial;
                font-weight: bold;
            }
            QPushButton#sendButton:hover {
                background: #e8dcc8;
                color: #8B7355;
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
                    self._send_message()
                    return True
                # Allow Shift+Enter for new line
                return False
        return super().eventFilter(obj, event)

    def _send_message(self):
        if not self._enabled:
            return
            
        if self._is_sending:
            # If currently sending, treat as stop button
            self.stop_requested.emit()
            return
            
        message = self.text_input.toPlainText().strip()
        if message:
            # Start loading state
            self._is_sending = True
            self.text_input.setEnabled(False)
            self.send_button.setText("⏹")
            self.send_button.setProperty("stop", True)
            self.send_button.style().unpolish(self.send_button)
            self.send_button.style().polish(self.send_button)
            self.send_button.setToolTip("Stop Octavia's response")
            
            # Emit message
            self.message_sent.emit(message)
            
            # Clear input and reset height
            self.text_input.clear()
            self._reset_height()

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
