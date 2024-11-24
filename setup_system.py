"""
Octavia System Setup Script
Initializes databases, memory system, and consciousness components
"""

import os
import sqlite3
import asyncio
from pathlib import Path
from loguru import logger

# Configure logging
logger.add("setup.log", rotation="1 MB")

class SystemSetup:
    def __init__(self):
        self.base_dir = Path(os.path.dirname(os.path.abspath(__file__)))
        self.data_dir = self.base_dir / "data"
        self.db_dir = self.data_dir / "db"
        
    def create_directories(self):
        """Create necessary directories"""
        logger.info("Creating system directories...")
        directories = [
            self.data_dir,
            self.db_dir,
            self.data_dir / "memory",
            self.data_dir / "logs",
            self.data_dir / "cache"
        ]
        
        for directory in directories:
            directory.mkdir(parents=True, exist_ok=True)
            logger.info(f"Created directory: {directory}")
            
    def setup_abilities_db(self):
        """Initialize the abilities tracking database"""
        logger.info("Setting up abilities database...")
        db_path = self.db_dir / "abilities.db"
        
        with sqlite3.connect(db_path) as conn:
            cursor = conn.cursor()
            
            # Create abilities table
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
            
            # Create ability metrics table
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
            logger.info("Abilities database initialized")
            
    def setup_tasks_db(self):
        """Initialize the task tracking database"""
        logger.info("Setting up tasks database...")
        db_path = self.db_dir / "tasks.db"
        
        with sqlite3.connect(db_path) as conn:
            cursor = conn.cursor()
            
            # Create tasks table
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
            
            # Create task dependencies table
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
            logger.info("Tasks database initialized")
            
    def setup_memory_db(self):
        """Initialize the memory patterns database"""
        logger.info("Setting up memory database...")
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
            logger.info("Memory database initialized")
            
    def run_setup(self):
        """Run the complete system setup"""
        try:
            logger.info("Starting Octavia system setup...")
            
            # Create necessary directories
            self.create_directories()
            
            # Setup databases
            self.setup_abilities_db()
            self.setup_tasks_db()
            self.setup_memory_db()
            
            logger.info("System setup completed successfully!")
            return True
            
        except Exception as e:
            logger.error(f"Error during system setup: {str(e)}")
            return False

if __name__ == "__main__":
    setup = SystemSetup()
    success = setup.run_setup()
    
    if success:
        print("\n✅ Octavia system setup completed successfully!")
        print("\nYou can now:")
        print("1. Launch the UI application")
        print("2. Enter your Gemini API key")
        print("3. Start interacting with Octavia")
    else:
        print("\n❌ System setup failed. Check setup.log for details.")
