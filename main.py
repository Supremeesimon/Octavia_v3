#!/usr/bin/env python3
"""
Main entry point for Octavia
"""

import sys
import asyncio
from loguru import logger
from PySide6.QtWidgets import QApplication

from src.interface.main_window import MainWindow

def main():
    """Main entry point for Octavia"""
    logger.info("Starting main application...")
    app = QApplication.instance()
    if not app:
        app = QApplication(sys.argv)
    
    window = MainWindow()
    window.show()
    
    # Run Qt event loop
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
