#!/usr/bin/env python3
"""
Octavia - Your AI Assistant
"""

import sys
import os
from pathlib import Path
import asyncio
import qasync
import traceback
import platform
import psutil
import signal
from PySide6.QtWidgets import QApplication
from PySide6.QtCore import Qt, QOperatingSystemVersion
from PySide6.QtGui import QIcon
from loguru import logger
import time

# Configure comprehensive logging
log_dir = Path(__file__).parent.parent / "logs"
log_dir.mkdir(exist_ok=True)
log_path = log_dir / "octavia.log"

# Remove default logger and set up our custom configuration
logger.remove()
logger.add(
    log_path,
    format="<green>{time:YYYY-MM-DD HH:mm:ss.SSS}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>",
    level="DEBUG",
    rotation="1 day",
    retention="7 days",
    backtrace=True,
    diagnose=True,
    enqueue=True,
    catch=True,
)
# Also log to stderr for immediate feedback
logger.add(
    sys.stderr,
    format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <level>{message}</level>",
    level="INFO",
    backtrace=True,
    diagnose=True,
)

# Add src to Python path
src_dir = Path(__file__).parent
sys.path.insert(0, str(src_dir))

def cleanup_existing_instances():
    """Clean up any existing Octavia instances"""
    current_pid = os.getpid()
    for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
        try:
            # Skip current process
            if proc.pid == current_pid:
                continue
                
            # Check if it's a Python process
            if proc.name().lower().startswith('python'):
                cmdline = proc.cmdline()
                # Check if it's running octavia.py
                if any('octavia.py' in arg.lower() for arg in cmdline):
                    logger.warning(f"Found existing Octavia instance (PID: {proc.pid}), terminating...")
                    proc.terminate()
                    try:
                        proc.wait(timeout=5)
                    except psutil.TimeoutExpired:
                        logger.warning(f"Process {proc.pid} did not terminate, killing...")
                        proc.kill()
        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
            continue

def cleanup_resources():
    """Clean up application resources"""
    try:
        # Add any cleanup code here
        pass
    except Exception as e:
        logger.error(f"Error during cleanup: {e}")

def signal_handler(signum, frame):
    """Handle termination signals"""
    logger.info(f"Received signal {signum}")
    cleanup_resources()
    sys.exit(0)

def configure_macos_app():
    """Configure macOS specific settings"""
    if platform.system() == "Darwin":
        logger.info("Configuring macOS specific settings...")
        try:
            # Set macOS app attributes
            QApplication.setApplicationName("Octavia")
            QApplication.setApplicationDisplayName("Octavia AI Assistant")
            QApplication.setOrganizationName("Codeium")
            QApplication.setOrganizationDomain("codeium.com")
            
            # Set app icon (assuming icon exists in resources)
            icon_path = Path(__file__).parent / "resources" / "icons" / "octavia.icns"
            if icon_path.exists():
                QApplication.setWindowIcon(QIcon(str(icon_path)))
            
            # Enable macOS features
            if QOperatingSystemVersion.current() >= QOperatingSystemVersion.MacOSBigSur:
                # Enable modern macOS styling
                QApplication.setStyle("macos")
            
            logger.info("macOS configuration complete")
        except Exception as e:
            logger.error(f"Error configuring macOS settings: {e}")

def exception_handler(type_, value, tb):
    """Global exception handler for uncaught exceptions"""
    logger.opt(exception=(type_, value, tb)).critical("Uncaught exception:")
    sys.__excepthook__(type_, value, tb)  # Call the default handler as well

async def main():
    """Main application entry point"""
    try:
        logger.info("Starting Octavia application...")
        
        # Set up exception handling
        sys.excepthook = exception_handler
        
        # Create Qt application instance
        app = QApplication.instance()
        if app is None:
            app = QApplication(sys.argv)
        else:
            logger.info("Using existing QApplication instance")
            
        # Configure macOS specific settings
        configure_macos_app()
        
        # Create and show main window
        logger.info("Creating main window")
        from interface.main_window import MainWindow
        window = MainWindow()
        window.show()
        
        logger.info("Starting event loop")
        
        # Create the event loop and run it
        loop = qasync.QEventLoop(app)
        asyncio.set_event_loop(loop)
        
        # Run the event loop
        with loop:
            return loop.run_forever()
        
    except Exception as e:
        logger.error(f"Error in event loop: {e}")
        traceback.print_exc()
        return 1
    finally:
        logger.info("Main window closed, cleaning up...")
        cleanup_resources()

if __name__ == "__main__":
    try:
        # Run the async main
        exit_code = asyncio.run(main())
        logger.info(f"Application exiting with code: {exit_code}")
        sys.exit(exit_code)
    except Exception as e:
        logger.error(f"Fatal error: {e}")
        traceback.print_exc()
        sys.exit(1)
