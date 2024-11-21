"""
Shared styles for Octavia UI components
"""

def get_global_styles():
    return """
        QMainWindow, QWidget {
            background-color: #F8EFD8;
            font-family: ".AppleSystemUIFont";
            color: #4a4a4a;
        }
        QWidget#leftPanel {
            background-color: #e8dcc8;
            border-top-right-radius: 10px;
            border-bottom-right-radius: 10px;
        }
        QLabel#sidebarHeader {
            font-size: 16px;
            font-weight: bold;
            color: #4a4a4a;
            padding: 0;
        }
        QPushButton#workspaceButton {
            background-color: transparent;
            border: none;
            border-radius: 6px;
            padding: 8px 12px;
            text-align: left;
            font-size: 14px;
            color: #4a4a4a;
        }
        QPushButton#workspaceButton:hover {
            background-color: #d8cbb8;
        }
        QPushButton#workspaceButton:pressed {
            background-color: #c8bba8;
        }
        QPushButton#workspaceButton[selected=true] {
            background-color: #d8cbb8;
            font-weight: bold;
        }
        QPushButton#addWorkspaceButton {
            background-color: transparent;
            border: 2px dashed #a8a8a8;
            border-radius: 6px;
            padding: 8px 12px;
            color: #666666;
            font-size: 14px;
        }
        QPushButton#addWorkspaceButton:hover {
            background-color: #d8cbb8;
            border-color: #666666;
            color: #4a4a4a;
        }
        QScrollArea#workspaceArea {
            background: transparent;
            border: none;
        }
        QScrollArea#workspaceArea > QWidget > QWidget {
            background: transparent;
        }
        QWidget#inputGroup {
            background-color: #e8dcc8;
            border-radius: 10px;
            min-height: 48px;
        }
        QWidget#rightContainer {
            background: transparent;
            border: none;
        }
        QWidget#modeContainer {
            background: transparent;
            border: none;
            margin-left: 4px;
        }
        QLabel#welcomeTitle {
            font-size: 28px;
            font-weight: bold;
            color: #4a4a4a;
            padding: 0;
            qproperty-alignment: AlignLeft;
        }
        QLabel#welcomeDescription {
            font-size: 18px;
            color: #666666;
            padding: 0;
            qproperty-alignment: AlignLeft;
        }
        QLabel#modeLabel {
            color: #666666;
            font-size: 11px;
            padding: 0 2px;
            min-width: 32px;
            qproperty-alignment: AlignCenter;  /* Keep mode labels centered */
        }
        QTextEdit#textInput {
            background-color: #e8dcc8;
            border: none;
            padding: 6px 10px;
            font-size: 14px;
            color: #4a4a4a;
            selection-background-color: #d8cbb8;
            border-radius: 10px;
        }
        QTextEdit#textInput:focus {
            border: none;
            outline: none;
        }
        QScrollBar:vertical {
            border: none;
            background: #e8dcc8;
            width: 8px;
            margin: 0px;
        }
        QScrollBar::handle:vertical {
            background: #d8cbb8;
            min-height: 20px;
            border-radius: 4px;
        }
        QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
            height: 0px;
        }
        QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical {
            background: none;
        }
        QPushButton#sendButton, QPushButton#attachButton {
            background-color: #e8dcc8;
            border: none;
            border-radius: 16px;
            margin: 0;
            padding: 0;
            min-width: 32px;
            min-height: 32px;
            max-width: 32px;
            max-height: 32px;
            color: #666666;
        }
        QPushButton#sendButton:hover, QPushButton#attachButton:hover {
            background-color: #d8cbb8;
            color: #4a4a4a;
        }
        QPushButton#sendButton {
            font-size: 18px;
            font-weight: bold;
        }
        QPushButton#attachButton {
            font-size: 16px;
        }
    """
