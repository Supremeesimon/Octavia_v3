"""
Text input component for Octavia
"""

from PySide6.QtWidgets import (QWidget, QHBoxLayout, QTextEdit, QPushButton,
                             QLabel, QVBoxLayout)
from PySide6.QtCore import Signal, Qt
from PySide6.QtGui import QPainter, QColor, QBrush

class ToggleSwitch(QWidget):
    toggled = Signal(bool)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedSize(36, 20)  
        self._is_checked = False
        self.animation_value = 0
        self.setToolTip("Switch between Action and Chat modes")

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        # Draw track 
        track_color = QColor("#4a4a4a") if self._is_checked else QColor("#666666")
        painter.setBrush(QBrush(track_color))
        painter.setPen(Qt.NoPen)
        painter.drawRoundedRect(0, 4, 36, 12, 6, 6)  

        # Draw handle 
        handle_x = 18 if self._is_checked else 2
        painter.setBrush(QBrush(QColor("#ffffff")))
        painter.drawEllipse(handle_x, 1, 18, 18)  

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self._is_checked = not self._is_checked
            self.update()
            self.toggled.emit(self._is_checked)

    def isChecked(self):
        return self._is_checked

    def setChecked(self, checked):
        if self._is_checked != checked:
            self._is_checked = checked
            self.update()
            self.toggled.emit(self._is_checked)

class TextInput(QWidget):
    message_sent = Signal(str)
    mode_changed = Signal(bool)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.action_mode = True
        self.setup_ui()
        self.setup_connections()

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
        content_widget = QWidget()
        content_layout = QHBoxLayout(content_widget)
        content_layout.setContentsMargins(8, 4, 8, 4)
        content_layout.setSpacing(4)

        # Text input
        self.text_input = QTextEdit()
        self.text_input.setObjectName("textInput")
        self.text_input.setPlaceholderText("Ask anything - use '@' to mention folder or file")
        self.text_input.setFixedHeight(36)
        self.text_input.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        content_layout.addWidget(self.text_input, 1)

        # Right side controls
        right_container = QWidget()
        right_container.setObjectName("rightContainer")
        right_container.setFixedWidth(220)  
        right_layout = QHBoxLayout(right_container)
        right_layout.setContentsMargins(0, 0, 0, 0)
        right_layout.setSpacing(8)

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

        # Mode toggle container with labels
        mode_container = QWidget()
        mode_container.setObjectName("modeContainer")
        mode_layout = QHBoxLayout(mode_container)
        mode_layout.setContentsMargins(0, 0, 0, 0)
        mode_layout.setSpacing(4)

        # Action mode label
        self.action_label = QLabel("Action")
        self.action_label.setObjectName("modeLabel")
        mode_layout.addWidget(self.action_label)

        # Custom toggle switch
        self.mode_toggle = ToggleSwitch()
        self.mode_toggle.setObjectName("modeToggle")
        mode_layout.addWidget(self.mode_toggle)

        # Chat mode label
        self.chat_label = QLabel("Chat")
        self.chat_label.setObjectName("modeLabel")
        mode_layout.addWidget(self.chat_label)

        right_layout.addWidget(mode_container)
        content_layout.addWidget(right_container)
        
        # Add the content widget to the main layout
        main_layout.addWidget(content_widget)

    def setup_connections(self):
        self.text_input.textChanged.connect(self._adjust_text_input_height)
        self.send_button.clicked.connect(self._on_send)
        self.mode_toggle.toggled.connect(self._on_mode_changed)

    def _adjust_text_input_height(self):
        doc_height = self.text_input.document().size().height()
        margins = self.text_input.contentsMargins()
        padding = 12
        
        new_height = doc_height + margins.top() + margins.bottom() + padding
        new_height = max(36, min(new_height, 200))  
        
        if new_height > 36:
            self.text_input.setFixedHeight(int(new_height))

    def _on_mode_changed(self, is_chat_mode):
        self.action_mode = not is_chat_mode
        if self.action_mode:
            self.text_input.setPlaceholderText("Ask anything - use '@' to mention folder or file")
        else:
            self.text_input.setPlaceholderText("Chat with Octavia (no actions will be taken)")
        self.mode_changed.emit(self.action_mode)

    def _on_send(self):
        message = self.text_input.toPlainText().strip()
        if message:
            self.message_sent.emit(message)
            self.text_input.clear()
            self.text_input.setFixedHeight(36)
            
    def is_action_mode(self):
        return self.action_mode
