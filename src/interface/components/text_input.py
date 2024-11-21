"""
Text input component for Octavia
"""

from PySide6.QtWidgets import (QWidget, QHBoxLayout, QTextEdit, QPushButton,
                              QVBoxLayout, QLabel)
from PySide6.QtCore import Signal, Qt, QTimer
from .toggle_switch import ToggleSwitch


class TextInput(QWidget):
    message_sent = Signal(str)
    mode_changed = Signal(bool)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.action_mode = True
        self.setup_ui()
        self.setup_connections()
        self._enabled = True
        self._is_sending = False

    def setup_ui(self):
        self.setObjectName("inputGroup")
        self.setFixedWidth(850)  
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

        # Send button
        self.send_button = QPushButton("→")  
        self.send_button.setObjectName("sendButton")
        self.send_button.setFixedSize(32, 32)  
        self.send_button.setToolTip("Send message")
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

    def _send_message(self):
        if not self._enabled or self._is_sending:
            return
            
        message = self.text_input.toPlainText().strip()
        if message:
            # Start loading state
            self._is_sending = True
            self.text_input.setEnabled(False)
            self.send_button.setText("•")
            self._loading_timer.start()
            
            # Emit message
            self.message_sent.emit(message)
            
            # Clear input
            self.text_input.clear()
            self._reset_height()

    def _update_loading_dots(self):
        """Update loading animation dots"""
        if not self._is_sending:
            self._loading_timer.stop()
            self.send_button.setText("→")
            return
            
        dots = "." * (self._loading_dots + 1)
        self.send_button.setText(dots)
        self._loading_dots = (self._loading_dots + 1) % 3

    def message_processed(self):
        """Call this when the message has been processed"""
        self._is_sending = False
        self.text_input.setEnabled(True)
        self._loading_timer.stop()
        self.send_button.setText("→")

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
