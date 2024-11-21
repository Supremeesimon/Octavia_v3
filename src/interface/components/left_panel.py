"""
Left panel component for Octavia
"""

from PySide6.QtWidgets import (QWidget, QVBoxLayout, QPushButton, 
                             QLabel, QScrollArea, QFrame)
from PySide6.QtCore import Qt, Signal

class LeftPanel(QWidget):
    """Left panel component containing workspace and project navigation"""
    
    workspace_selected = Signal(str)  # Emitted when workspace is selected
    project_selected = Signal(str)    # Emitted when project is selected
    
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
        
        # Add workspace button
        add_workspace_btn = QPushButton("+ New Workspace")
        add_workspace_btn.setObjectName("addWorkspaceButton")
        layout.addWidget(add_workspace_btn)
        
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
