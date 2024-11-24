#!/usr/bin/env python3
"""
Octavia Unified Runner
Combines setup and runtime functionality in a single script.
"""

import os
import sys
import sqlite3
import asyncio
from pathlib import Path
from loguru import logger
from qasync import QEventLoop
from PySide6.QtWidgets import QApplication
from src.interface.main_window import MainWindow

class OctaviaSystem:
    def __init__(self):
        self.base_dir = Path(os.path.dirname(os.path.abspath(__file__)))
        self.data_dir = self.base_dir / "data"
        self.db_dir = self.data_dir / "db"
        self.log_dir = self.data_dir / "logs"
        
        # Ensure log directory exists
        self.log_dir.mkdir(parents=True, exist_ok=True)
        
        # Configure logging
        logger.remove()
        logger.add(sys.stderr, level="INFO")
        logger.add(self.log_dir / "octavia.log", rotation="1 day", retention="7 days", level="DEBUG")
        logger.add(self.log_dir / "setup.log", rotation="1 MB", level="DEBUG")  # Separate setup log
        self.logger = logger.bind(name="Octavia")
        
        # Add src to Python path
        src_path = self.base_dir / "src"
        sys.path.append(str(src_path))
        
    def create_directories(self):
        """Create necessary directories"""
        self.logger.info("Creating system directories...")
        directories = [
            self.data_dir,
            self.db_dir,
            self.data_dir / "memory",
            self.data_dir / "logs",
            self.data_dir / "cache"
        ]
        
        for directory in directories:
            directory.mkdir(parents=True, exist_ok=True)
            self.logger.info(f"Created directory: {directory}")
            
    def setup_abilities_db(self):
        """Initialize the abilities tracking database"""
        self.logger.info("Setting up abilities database...")
        db_path = self.db_dir / "abilities.db"
        
        with sqlite3.connect(db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS abilities (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL UNIQUE,
                    description TEXT,
                    ability_type TEXT NOT NULL,
                    requirements TEXT,
                    metadata TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS ability_metrics (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    ability_id INTEGER NOT NULL,
                    success BOOLEAN NOT NULL,
                    response_time FLOAT,
                    context TEXT,
                    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (ability_id) REFERENCES abilities (id)
                )
            """)
            conn.commit()
            self.logger.info("Abilities database initialized")
            
    def setup_tasks_db(self):
        """Initialize the task tracking database"""
        self.logger.info("Setting up tasks database...")
        db_path = self.db_dir / "tasks.db"
        
        with sqlite3.connect(db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS tasks (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    title TEXT NOT NULL,
                    description TEXT,
                    status TEXT NOT NULL,
                    priority TEXT NOT NULL,
                    context TEXT,
                    parent_id INTEGER,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (parent_id) REFERENCES tasks (id)
                )
            """)
            
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS task_dependencies (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    task_id INTEGER NOT NULL,
                    depends_on_id INTEGER NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (task_id) REFERENCES tasks (id),
                    FOREIGN KEY (depends_on_id) REFERENCES tasks (id)
                )
            """)
            conn.commit()
            self.logger.info("Tasks database initialized")

    def setup_memory_db(self):
        """Initialize the memory patterns database"""
        self.logger.info("Setting up memory database...")
        db_path = self.db_dir / "memory.db"
        
        with sqlite3.connect(db_path) as conn:
            cursor = conn.cursor()
            
            # Create memory patterns table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS memory_patterns (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    pattern_type TEXT NOT NULL,
                    pattern_data TEXT NOT NULL,
                    confidence FLOAT,
                    frequency INTEGER DEFAULT 1,
                    last_accessed TIMESTAMP,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # Create pattern relationships table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS pattern_relationships (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    pattern_id INTEGER NOT NULL,
                    related_pattern_id INTEGER NOT NULL,
                    relationship_type TEXT NOT NULL,
                    strength FLOAT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (pattern_id) REFERENCES memory_patterns (id),
                    FOREIGN KEY (related_pattern_id) REFERENCES memory_patterns (id)
                )
            """)
            
            conn.commit()
            self.logger.info("Memory database initialized")
    
    def setup_system(self):
        """Run first-time system setup"""
        try:
            self.logger.info("Starting system setup...")
            self.create_directories()
            self.setup_abilities_db()
            self.setup_tasks_db()
            self.setup_memory_db()
            self.logger.info("System setup completed successfully")
            return True
        except Exception as e:
            self.logger.error(f"Error during system setup: {str(e)}")
            return False
    
    def check_environment(self):
        """Check and set required environment variables"""
        # No need to check for API key since it's provided through UI
        pass
            
    def run_error(self, error_msg: str) -> int:
        """Handle run errors consistently"""
        self.logger.error(f"Error running Octavia: {error_msg}")
        if not any(handler.name == "stderr" for handler in logger._core.handlers):
            print(f"\n❌ Error: {error_msg}")
        return 1
            
    async def run(self):
        """Main entry point for running Octavia"""
        try:
            self.logger.info("Starting Octavia...")
            self.check_environment()
            
            # Create Qt application
            app = QApplication(sys.argv)
            
            # Create event loop
            loop = QEventLoop(app)
            asyncio.set_event_loop(loop)
            
            # Create and show main window
            window = MainWindow()
            window.show()
            
            # Enter event loop
            with loop:
                self.logger.info("Octavia is running...")
                loop.run_forever()  # Run forever
                
        except Exception as e:
            return self.run_error(str(e))
        return 0

def main():
    """Entry point for both setup and running"""
    try:
        octavia = OctaviaSystem()
        
        # Run setup if this is first time
        first_time_setup = not (octavia.db_dir / "abilities.db").exists()
        if first_time_setup:
            if not octavia.setup_system():
                print("\n❌ System setup failed. Check setup.log for details.")
                return 1
            print("\n✅ Octavia system setup completed successfully!")
            print("\nYou can now:")
            print("1. Launch the UI application")
            print("2. Enter your Gemini API key in the UI")
            print("3. Start interacting with Octavia")
        
        # Create new event loop and run Octavia
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        return loop.run_until_complete(octavia.run())
        
    except Exception as e:
        print(f"\n❌ Fatal error: {str(e)}")
        return 1

if __name__ == "__main__":
    sys.exit(main())
