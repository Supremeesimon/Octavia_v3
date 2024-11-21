"""
Left panel component for Octavia
"""

from PySide6.QtWidgets import (QWidget, QVBoxLayout, QPushButton, 
                             QLabel, QScrollArea, QFrame, QLineEdit)
from PySide6.QtCore import Qt, Signal

class LeftPanel(QWidget):
    """Left panel component containing workspace navigation"""
    
    workspace_selected = Signal(str)  # Emitted when workspace is selected
    api_key_inserted = Signal(str)    # Emitted when API key is inserted
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("leftPanel")
        self.setFixedWidth(300)
        self.setup_ui()
        
    def setup_ui(self):
        """Setup the left panel UI"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(16)
        
        # Header section
        header = QLabel("Workspaces")
        header.setObjectName("sidebarHeader")
        layout.addWidget(header)
        
        # Workspace section
        workspace_area = QScrollArea()
        workspace_area.setObjectName("workspaceArea")
        workspace_area.setWidgetResizable(True)
        workspace_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        workspace_area.setFrameShape(QFrame.NoFrame)
        
        workspace_container = QWidget()
        self.workspace_layout = QVBoxLayout(workspace_container)
        self.workspace_layout.setContentsMargins(0, 0, 0, 0)
        self.workspace_layout.setSpacing(8)
        self.workspace_layout.addStretch()
        
        workspace_area.setWidget(workspace_container)
        layout.addWidget(workspace_area)
        
        # Add stretch to push API key section to bottom
        layout.addStretch()
        
        # API Key section
        self.api_key_input = QLineEdit()
        self.api_key_input.setObjectName("apiKeyInput")
        self.api_key_input.setPlaceholderText("Enter activation key...")
        self.api_key_input.setEchoMode(QLineEdit.Password)
        layout.addWidget(self.api_key_input)
        
        self.insert_key_btn = QPushButton("Insert")
        self.insert_key_btn.setObjectName("insertKeyButton")
        self.insert_key_btn.clicked.connect(self._handle_key_insert)
        layout.addWidget(self.insert_key_btn)
        
        self.api_status = QLabel("")
        self.api_status.setObjectName("apiKeyStatus")
        self.api_status.hide()
        layout.addWidget(self.api_status)
        
    def _handle_key_insert(self):
        """Handle API key insertion"""
        key = self.api_key_input.text().strip()
        if key:
            self.api_key_inserted.emit(key)
            self.api_key_input.clear()
            self.api_key_input.setEnabled(False)
            self.insert_key_btn.hide()
            self.api_status.setText("✓ Activated")
            self.api_status.show()
            
    def add_workspace(self, name: str):
        """Add a workspace button to the panel"""
        workspace_btn = QPushButton(name)
        workspace_btn.setObjectName("workspaceButton")
        workspace_btn.clicked.connect(lambda: self.workspace_selected.emit(name))
        # Insert before the stretch
        self.workspace_layout.insertWidget(self.workspace_layout.count() - 1, workspace_btn)
        
    def clear_workspaces(self):
        """Clear all workspace buttons"""
        while self.workspace_layout.count() > 1:  # Keep the stretch
            item = self.workspace_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
