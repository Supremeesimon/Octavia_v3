"""
Octavia's Main Window Interface - Based on Modern React Design
"""

import sys
from pathlib import Path
from loguru import logger
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLineEdit, QPushButton, QLabel, QCheckBox, QScrollArea,
    QFrame, QStackedWidget, QTextEdit, QGraphicsOpacityEffect,
    QListWidget, QListWidgetItem, QRadioButton
)
from PySide6.QtCore import Qt, Signal, Slot, QTimer, QSize, QPoint, QPropertyAnimation, QEasingCurve
from PySide6.QtGui import QIcon, QFont, QPainter, QColor, QPalette, QMouseEvent


class OctaviaState:
    """Global state management for Octavia"""
    def __init__(self):
        self.write_mode = True
        self.gemini_flash_visible = False
        self.search_query = ""
        self.input_value = ""
        self.checked_items = {
            'manageFolders': True,
            'openCommandPalette': False,
            'foldersSecurity': True,
            'triggerCommand': False
        }
        self.past_workflows = [
            {"name": "Octavia: AI File Management System", "time": "23m"},
            {"name": "Intelligent Voice Folder Manager", "time": "17h"},
            {"name": "Octavia AI Assistant Design", "time": "19h"},
        ]

    def toggle_mode(self):
        self.write_mode = not self.write_mode
        return self.write_mode


class AnimatedWidget(QWidget):
    """Base class for widgets with animation support"""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.opacity_effect = QGraphicsOpacityEffect(self)
        self.setGraphicsEffect(self.opacity_effect)
        self.opacity_animation = QPropertyAnimation(self.opacity_effect, b"opacity")
        self.opacity_animation.setDuration(700)  # Match React's 0.7s
        self.opacity_animation.setEasingCurve(QEasingCurve.InOutQuad)

    def fade_in(self):
        self.opacity_animation.setStartValue(0)
        self.opacity_animation.setEndValue(1)
        self.opacity_animation.start()

    def fade_out(self):
        self.opacity_animation.setStartValue(1)
        self.opacity_animation.setEndValue(0)
        self.opacity_animation.start()


class WindowControlButton(QPushButton):
    """Custom window control button (close, minimize, maximize)"""
    def __init__(self, color, parent=None):
        super().__init__(parent)
        self.setFixedSize(12, 12)
        self.setStyleSheet(f"""
            QPushButton {{
                background-color: {color};
                border-radius: 6px;
                border: none;
            }}
            QPushButton:hover {{
                background-color: {color};
                opacity: 0.8;
            }}
        """)


class IconButton(QPushButton):
    """Custom icon button with hover effects"""
    def __init__(self, icon_path, parent=None):
        super().__init__(parent)
        self.setFixedSize(24, 24)
        icon_file = str(Path(__file__).parent / "icons" / f"{icon_path}.svg")
        self.setIcon(QIcon(icon_file))
        self.setIconSize(QSize(12, 12))
        self.setStyleSheet("""
            QPushButton {
                background-color: #e8dcc8;
                border-radius: 4px;
                border: none;
            }
            QPushButton:hover {
                background-color: #e0d4c0;
            }
        """)


class SidebarButton(QPushButton):
    """Narrow sidebar button with icon"""
    def __init__(self, icon_path, parent=None):
        super().__init__(parent)
        self.setFixedSize(24, 24)
        icon_file = str(Path(__file__).parent / "icons" / f"{icon_path}.svg")
        self.setIcon(QIcon(icon_file))
        self.setIconSize(QSize(12, 12))
        self.setStyleSheet("""
            QPushButton {
                background-color: #e8dcc8;
                border-radius: 4px;
                border: none;
                margin: 4px 0;
            }
            QPushButton:hover {
                background-color: #e0d4c0;
            }
        """)


class TopBar(QWidget):
    """Top bar with window controls and search"""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent = parent
        layout = QHBoxLayout(self)
        layout.setContentsMargins(16, 4, 16, 4)

        # Window controls
        controls = QHBoxLayout()
        controls.setSpacing(6)
        colors = ["#ff5f57", "#ffbd2e", "#28c840"]  # Red, Yellow, Green
        self.window_buttons = []
        for color in colors:
            btn = WindowControlButton(color)
            self.window_buttons.append(btn)
            controls.addWidget(btn)
        layout.addLayout(controls)

        # Search bar
        search = QLineEdit()
        search.setPlaceholderText("Octavia_v2")
        search.setFixedWidth(200)
        search.setStyleSheet("""
            QLineEdit {
                border: none;
                background-color: transparent;
                font-size: 12px;
                padding: 4px;
            }
        """)
        layout.addWidget(search, alignment=Qt.AlignCenter)

        # Right icons
        icons_layout = QHBoxLayout()
        icons_layout.setSpacing(8)
        for icon in ["layout", "box", "command", "bell", "settings"]:
            icons_layout.addWidget(IconButton(icon))
        layout.addLayout(icons_layout)

        # Connect window control buttons
        self.window_buttons[0].clicked.connect(self.parent.close)
        self.window_buttons[1].clicked.connect(self.parent.showMinimized)
        self.window_buttons[2].clicked.connect(self.toggle_maximize)

    def toggle_maximize(self):
        if self.parent.isMaximized():
            self.parent.showNormal()
        else:
            self.parent.showMaximized()

    def mousePressEvent(self, event: QMouseEvent):
        if event.button() == Qt.LeftButton:
            self.parent.drag_position = event.globalPosition().toPoint() - self.parent.pos()
            event.accept()

    def mouseMoveEvent(self, event: QMouseEvent):
        if event.buttons() & Qt.LeftButton and not self.parent.isMaximized():
            self.parent.move(event.globalPosition().toPoint() - self.parent.drag_position)
            event.accept()


class LeftSidebar(QWidget):
    """Narrow left sidebar with icons"""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedWidth(48)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(12, 16, 12, 16)
        layout.setSpacing(0)

        for icon in ["search", "share2", "git-branch", "box", "layout", "beaker", "thumbs-up"]:
            layout.addWidget(SidebarButton(icon))

        layout.addStretch()


class LeftPanel(QWidget):
    """Wide left panel with settings"""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedWidth(256)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(12)

        # Title section
        title = QLabel("Windsurf")
        title.setProperty("title", True)
        title.setStyleSheet("""
            font-size: 20px;
            font-weight: bold;
        """)
        layout.addWidget(title)

        subtitle = QLabel("Getting started with Windsurf")
        subtitle.setProperty("hint", True)
        subtitle.setStyleSheet("font-size: 14px;")
        layout.addWidget(subtitle)

        # Options with radio buttons
        options_frame = QFrame()
        options_frame.setStyleSheet("background: transparent;")
        options_layout = QVBoxLayout(options_frame)
        options_layout.setSpacing(12)
        options_layout.setContentsMargins(0, 8, 0, 8)

        # First set of options
        for option, shortcut, checked in [
            ("Code with Cascade", "⌘L", True),
            ("Open Command Palette", "⌘P", False)
        ]:
            option_widget = QWidget()
            option_layout = QHBoxLayout(option_widget)
            option_layout.setContentsMargins(0, 0, 0, 0)
            option_layout.setSpacing(12)

            radio = QRadioButton()
            radio.setChecked(checked)
            option_layout.addWidget(radio)

            label = QLabel(option)
            label.setProperty("workflow-title" if checked else "subtitle", True)
            label.setStyleSheet("font-size: 13px;")
            option_layout.addWidget(label)

            shortcut_label = QLabel(shortcut)
            shortcut_label.setProperty("shortcut", True)
            option_layout.addWidget(shortcut_label, alignment=Qt.AlignRight)
            option_layout.addStretch()

            options_layout.addWidget(option_widget)

        # Progress indicator
        progress_widget = QWidget()
        progress_layout = QVBoxLayout(progress_widget)
        progress_layout.setContentsMargins(0, 8, 0, 8)
        progress_layout.setSpacing(4)
        
        progress_label = QLabel("50% done")
        progress_label.setProperty("progress", True)
        progress_layout.addWidget(progress_label)
        
        progress_bar = QFrame()
        progress_bar.setFixedHeight(4)
        progress_bar.setStyleSheet("""
            QFrame {
                background-color: #EEEBDD;
                border-radius: 2px;
            }
        """)
        progress_layout.addWidget(progress_bar)
        
        progress_fill = QFrame(progress_bar)
        progress_fill.setFixedSize(progress_bar.width() * 0.5, 4)
        progress_fill.setStyleSheet("""
            QFrame {
                background-color: #333333;
                border-radius: 2px;
            }
        """)
        
        options_layout.addWidget(progress_widget)

        # Additional options
        for option, shortcut in [
            ("Code with Cascade", "⌘L"),
            ("Trigger Command while Editing Code", "I")
        ]:
            option_widget = QWidget()
            option_layout = QHBoxLayout(option_widget)
            option_layout.setContentsMargins(0, 0, 0, 0)
            option_layout.setSpacing(12)

            label = QLabel(option)
            label.setProperty("subtitle", True)
            label.setStyleSheet("font-size: 13px;")
            option_layout.addWidget(label)

            shortcut_label = QLabel(shortcut)
            shortcut_label.setProperty("shortcut", True)
            option_layout.addWidget(shortcut_label, alignment=Qt.AlignRight)
            option_layout.addStretch()

            options_layout.addWidget(option_widget)

        layout.addWidget(options_frame)
        layout.addStretch()


class GeminiFlash(AnimatedWidget):
    """Animated Gemini Flash intelligence indicator"""
    def __init__(self, parent=None):
        super().__init__(parent)
        layout = QVBoxLayout(self)

        # Container with custom styling
        container = QFrame()
        container.setStyleSheet("""
            QFrame {
                background-color: #e8dcc8;
                border-radius: 12px;
                padding: 16px;
            }
        """)
        container_layout = QVBoxLayout(container)

        # Header with spinner
        header = QHBoxLayout()
        spinner = LoadingSpinner()
        header.addWidget(spinner)

        title = QLabel("Gemini 1.5 Flash Intelligence")
        title.setStyleSheet("font-weight: bold; font-size: 14px;")
        header.addWidget(title)
        header.addStretch()

        container_layout.addLayout(header)
        layout.addWidget(container)

        # Start hidden
        self.setVisible(False)


class LoadingSpinner(QWidget):
    """Animated loading spinner"""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedSize(24, 24)
        self.angle = 0

        self.timer = QTimer(self)
        self.timer.timeout.connect(self.rotate)
        self.timer.start(50)  # Update every 50ms

        self.setStyleSheet("""
            background-color: #teal-100;
            border-radius: 12px;
        """)

    def rotate(self):
        self.angle = (self.angle + 10) % 360
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        # Draw spinner
        pen = painter.pen()
        pen.setWidth(2)
        pen.setColor(QColor("#14b8a6"))  # teal-500
        painter.setPen(pen)

        painter.translate(12, 12)
        painter.rotate(self.angle)
        painter.drawArc(-8, -8, 16, 16, 0, 5040)  # 5040 = 7/8 of 5760 (16 * 360)


class MainContent(AnimatedWidget):
    """Enhanced main content area with animations"""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.state = OctaviaState()
        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 24, 24, 24)

        # Mode indicator with animation
        mode_row = QHBoxLayout()
        self.mode_label = QLabel("Windsurf | Write mode") # Changed label
        self.mode_label.setStyleSheet("""
            font-size: 12px;
            padding: 4px 8px;
            background-color: #e8dcc8;
            border-radius: 4px;
        """)
        mode_row.addWidget(self.mode_label)

        shortcut = QLabel("⌘")
        shortcut.setStyleSheet("""
            font-size: 10px;
            padding: 2px 4px;
            background-color: #e8dcc8;
            border-radius: 4px;
        """)
        mode_row.addWidget(shortcut)
        mode_row.addStretch()
        layout.addLayout(mode_row)

        # Centered content
        center_content = QVBoxLayout()
        center_content.setAlignment(Qt.AlignCenter)

        # Animated logo
        self.logo_spinner = LoadingSpinner()
        self.logo_spinner.setFixedSize(48, 48)
        center_content.addWidget(self.logo_spinner, alignment=Qt.AlignCenter)

        # Welcome text
        welcome = QLabel("Write with Cascade") # Changed label
        welcome.setStyleSheet("font-size: 18px; font-weight: bold; margin: 16px 0 8px 0;")
        welcome.setAlignment(Qt.AlignCenter)
        center_content.addWidget(welcome)

        subtitle = QLabel("Kick off a new project or make changes across your entire codebase") # Changed label
        subtitle.setStyleSheet("font-size: 12px; color: #666; margin-bottom: 8px;")
        subtitle.setAlignment(Qt.AlignCenter)
        center_content.addWidget(subtitle)

        # Try it out link
        try_link = QLabel("New to Cascade? <a href='#' style='color: #666;'>Try it out with a test workspace</a>") # Changed label
        try_link.setStyleSheet("font-size: 12px; color: #666;")
        try_link.setAlignment(Qt.AlignCenter)
        try_link.setOpenExternalLinks(False)
        center_content.addWidget(try_link)

        layout.addLayout(center_content)

        # Input area
        input_frame = QFrame()
        input_frame.setStyleSheet("""
            QFrame {
                background-color: #e8dcc8;
                border-radius: 12px;
                padding: 8px;
                margin-top: 24px;
            }
        """)
        input_layout = QVBoxLayout(input_frame)
        input_layout.setContentsMargins(8, 8, 8, 8)
        input_layout.setSpacing(0)

        text_input = QTextEdit()
        text_input.setPlaceholderText("Ask anything - use '@' to mention code blocks")
        text_input.setStyleSheet("""
            QTextEdit {
                border: none;
                background-color: transparent;
                font-size: 14px;
                min-height: 80px;
                padding: 4px;
            }
            QTextEdit:focus {
                outline: none;
            }
        """)
        text_input.setFixedHeight(80)
        input_layout.addWidget(text_input)

        layout.addWidget(input_frame)

        # Gemini Flash
        self.gemini_flash = GeminiFlash()
        layout.addWidget(self.gemini_flash)

        # Show Gemini Flash after delay
        QTimer.singleShot(1500, self.show_gemini_flash)

        # Past Workflows
        workflows_frame = QFrame()
        workflows_frame.setStyleSheet("""
            QFrame {
                background-color: #e8dcc8;
                border-radius: 12px;
                padding: 8px;
                margin-top: 24px;
            }
        """)
        workflows_layout = QVBoxLayout(workflows_frame)
        workflows_title = QLabel("Past workflows")
        workflows_layout.addWidget(workflows_title)
        self.workflows_list = QListWidget()
        workflows_layout.addWidget(self.workflows_list)
        layout.addWidget(workflows_frame)
        self.populate_workflows()

        layout.addStretch()

    def populate_workflows(self):
        for workflow in self.state.past_workflows:
            item = QListWidgetItem(f"{workflow['name']}  {workflow['time']}")
            self.workflows_list.addItem(item)

    def show_gemini_flash(self):
        self.gemini_flash.setVisible(True)
        self.gemini_flash.fade_in()


class MainWindow(QMainWindow):
    """Main window for Octavia"""
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Windsurf")
        self.setMinimumSize(1200, 800)
        self.setStyleSheet("""
            QMainWindow, QWidget {
                background-color: #F8EFD8;
            }
            QLabel {
                color: #333333;
            }
            QLabel[title="true"] {
                color: #000000;
                font-weight: bold;
            }
            QLabel[subtitle="true"] {
                color: #666666;
            }
            QLabel[hint="true"] {
                color: #AAAAAA;
            }
            QPushButton {
                background-color: transparent;
                border: none;
                color: #6E6E6E;
                padding: 8px;
            }
            QPushButton:hover {
                color: #000000;
            }
            QLabel[shortcut="true"] {
                background-color: #EEEBDD;
                color: #333333;
                padding: 4px 8px;
                border-radius: 4px;
                font-size: 12px;
            }
            QLabel[link="true"] {
                color: #007ACC;
                text-decoration: underline;
            }
            QRadioButton::indicator {
                width: 16px;
                height: 16px;
                border-radius: 8px;
                border: 2px solid #CCCCCC;
            }
            QRadioButton::indicator:checked {
                border: 2px solid #333333;
                background-color: #000000;
            }
            QLabel[progress="true"] {
                color: #333333;
                font-weight: medium;
            }
            QLabel[workflow-title="true"] {
                color: #000000;
                font-weight: bold;
            }
            QLabel[workflow-time="true"] {
                color: #AAAAAA;
            }
        """)

        # Create main widget and layout
        main_widget = QWidget()
        main_layout = QVBoxLayout(main_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # Add top bar
        self.top_bar = TopBar(self)
        main_layout.addWidget(self.top_bar)

        # Create content area
        content = QHBoxLayout()
        content.setContentsMargins(0, 0, 0, 0)
        content.setSpacing(0)

        # Add sidebars and main content
        left_sidebar = LeftSidebar()
        left_sidebar.setFixedWidth(64)  # Adjusted width
        content.addWidget(left_sidebar)

        left_panel = LeftPanel()
        content.addWidget(left_panel)

        main_content = MainContent()
        main_content.setFixedWidth(600)  # Adjusted width
        content.addWidget(main_content)

        main_layout.addLayout(content)

        # Bottom bar
        bottom_bar = QWidget()
        bottom_bar.setFixedHeight(32)
        bottom_bar.setStyleSheet("""
            QWidget {
                background-color: #f0e6d2;
                border-top: 1px solid #e0d4c0;
            }
        """)
        bottom_layout = QHBoxLayout(bottom_bar)
        bottom_layout.setContentsMargins(16, 0, 16, 0)

        stats = QLabel("0 △ 0")
        stats.setStyleSheet("font-size: 10px;")
        bottom_layout.addWidget(stats)

        bottom_layout.addStretch()

        settings = QLabel("Windsurf Settings")  # Changed label
        settings.setStyleSheet("font-size: 10px;")
        bottom_layout.addWidget(settings)

        main_layout.addWidget(bottom_bar)

        # Set central widget
        self.setCentralWidget(main_widget)

        # Remove window frame
        self.setWindowFlags(Qt.FramelessWindowHint)
        self.drag_position = QPoint()


def main():
    """Main entry point for the application"""
    try:
        app = QApplication.instance()
        if not app:
            app = QApplication(sys.argv)

        # Set application style
        app.setStyle('Fusion')

        # Create and show window
        window = MainWindow()
        window.show()

        return app.exec()
    except Exception as e:
        logger.error(f"Fatal error in main: {e}")
        return 1


if __name__ == "__main__":
    main()
