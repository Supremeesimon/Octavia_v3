"""
Octavia's Main Window Interface
"""

import sys
import os
from PySide6.QtWidgets import QMainWindow, QWidget, QHBoxLayout, QVBoxLayout, QApplication
from PySide6.QtCore import Qt

# Add the src directory to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from interface.components import WelcomeSection, TextInput, OctaviaState, get_global_styles, LeftPanel

class MainWindow(QMainWindow):
    """Main window for Octavia"""
    def __init__(self):
        super().__init__()
        self.state = OctaviaState()
        self.setWindowTitle("Octavia")
        self.setMinimumSize(1200, 800)
        
        # Apply styles from external stylesheet
        self.setStyleSheet(get_global_styles())
        
        # Setup main layout
        main_widget = QWidget()
        main_layout = QHBoxLayout(main_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        
        # Create left sidebar
        self.left_panel = LeftPanel()
        self.left_panel.workspace_selected.connect(self._handle_workspace_selected)
        self.left_panel.project_selected.connect(self._handle_project_selected)
        main_layout.addWidget(self.left_panel)
        
        # Create main content area
        right_panel = self._setup_main_content()
        main_layout.addWidget(right_panel)
        
        self.setCentralWidget(main_widget)
        
        # Add test workspaces
        self._add_test_workspaces()

    def _setup_main_content(self):
        """Setup the main content area with welcome message and input"""
        right_panel = QWidget()
        layout = QVBoxLayout(right_panel)
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(20)

        # Container for both welcome and input
        content_container = QWidget()
        content_layout = QVBoxLayout(content_container)
        content_layout.setContentsMargins(0, 0, 0, 0)
        content_layout.setSpacing(20)

        # Welcome section
        welcome = WelcomeSection()
        welcome.setFixedWidth(850)  # Match text input width
        content_layout.addWidget(welcome)
        
        # Text input
        text_input = TextInput()
        text_input.message_sent.connect(self._handle_message)
        content_layout.addWidget(text_input)
        
        # Center the content container
        container_wrapper = QHBoxLayout()
        container_wrapper.addStretch()
        container_wrapper.addWidget(content_container)
        container_wrapper.addStretch()
        
        layout.addLayout(container_wrapper)
        layout.addStretch()
        
        return right_panel

    def _handle_message(self, message: str):
        """Handle messages sent from the text input"""
        print(f"Message received: {message}")  # For now, just print the message

    def _handle_workspace_selected(self, workspace: str):
        """Handle workspace selection"""
        print(f"Workspace selected: {workspace}")
        self.state.current_workspace = workspace

    def _handle_project_selected(self, project: str):
        """Handle project selection"""
        print(f"Project selected: {project}")
        self.state.current_project = project
        
    def _add_test_workspaces(self):
        """Add some test workspaces for development"""
        test_workspaces = ["Personal", "Work", "Projects"]
        for workspace in test_workspaces:
            self.left_panel.add_workspace(workspace)


def main():
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
