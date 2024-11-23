#!/usr/bin/env python3
"""
Octavia Runner Script
This script provides a reliable way to start Octavia with proper environment setup.
"""

import os
import sys
import asyncio
import logging
from qasync import QEventLoop
from PySide6.QtWidgets import QApplication
from loguru import logger
from src.interface.main_window import MainWindow

# Create logs directory if it doesn't exist
log_dir = os.path.join(os.path.dirname(__file__), "logs")
os.makedirs(log_dir, exist_ok=True)

# Configure logging
logger.remove()
logger.add(sys.stderr, level="INFO")
logger.add(os.path.join(log_dir, 'octavia.log'), rotation="1 day", retention="7 days", level="DEBUG")

logger = logger.bind(name="OctaviaRunner")

def main():
    """Main entry point for Octavia"""
    try:
        logger.info("Starting Octavia...")
        
        # Create application instance
        app = QApplication(sys.argv)
        
        # Create event loop
        loop = QEventLoop(app)
        asyncio.set_event_loop(loop)
        
        # Create and show main window
        window = MainWindow()
        window.show()
        
        # Enter event loop
        with loop:
            loop.run_forever()
            
    except Exception as e:
        logger.error(f"Error starting Octavia: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()
