"""
Octavia's Context Management System
"""

import json
import sqlite3
from typing import Dict, Optional
from datetime import datetime
from pathlib import Path
from loguru import logger

class ContextManager:
    """Manages Octavia's understanding of context and state"""
    
    def __init__(self, db_path: Optional[str] = None):
        """Initialize context manager with database connection"""
        if db_path is None:
            db_path = Path.home() / ".octavia" / "context.db"
        
        # Ensure directory exists
        db_path.parent.mkdir(parents=True, exist_ok=True)
        
        self.db_path = db_path
        self._init_database()
        logger.info(f"Initialized Context Manager with database at {db_path}")

    def _init_database(self):
        """Initialize SQLite database with required tables"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # Create tables for different types of context
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS system_state (
                        id INTEGER PRIMARY KEY,
                        timestamp TEXT,
                        state_data TEXT
                    )
                """)
                
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS user_preferences (
                        id INTEGER PRIMARY KEY,
                        timestamp TEXT,
                        preferences TEXT
                    )
                """)
                
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS conversation_history (
                        id INTEGER PRIMARY KEY,
                        timestamp TEXT,
                        user_message TEXT,
                        assistant_message TEXT
                    )
                """)
                
                conn.commit()
                logger.info("Successfully initialized context database")
        except Exception as e:
            logger.error(f"Failed to initialize database: {e}")
            raise

    async def get_current_context(self) -> Dict:
        """Get the current context including system state and user preferences"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # Get latest system state
                cursor.execute("""
                    SELECT state_data FROM system_state 
                    ORDER BY timestamp DESC LIMIT 1
                """)
                system_state = cursor.fetchone()
                
                # Get latest user preferences
                cursor.execute("""
                    SELECT preferences FROM user_preferences 
                    ORDER BY timestamp DESC LIMIT 1
                """)
                preferences = cursor.fetchone()
                
                return {
                    'system_state': json.loads(system_state[0]) if system_state else {},
                    'user_preferences': json.loads(preferences[0]) if preferences else {}
                }
        except Exception as e:
            logger.error(f"Error getting current context: {e}")
            return {'system_state': {}, 'user_preferences': {}}

    async def update_system_state(self, state: Dict):
        """Update the system state"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    INSERT INTO system_state (timestamp, state_data)
                    VALUES (?, ?)
                """, (datetime.now().isoformat(), json.dumps(state)))
                conn.commit()
                logger.info("Successfully updated system state")
        except Exception as e:
            logger.error(f"Error updating system state: {e}")
            raise

    async def update_user_preferences(self, preferences: Dict):
        """Update user preferences"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    INSERT INTO user_preferences (timestamp, preferences)
                    VALUES (?, ?)
                """, (datetime.now().isoformat(), json.dumps(preferences)))
                conn.commit()
                logger.info("Successfully updated user preferences")
        except Exception as e:
            logger.error(f"Error updating user preferences: {e}")
            raise

    async def add_conversation_entry(self, user_message: str, assistant_message: str):
        """Add a conversation exchange to history"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    INSERT INTO conversation_history 
                    (timestamp, user_message, assistant_message)
                    VALUES (?, ?, ?)
                """, (datetime.now().isoformat(), user_message, assistant_message))
                conn.commit()
                logger.info("Successfully added conversation entry")
        except Exception as e:
            logger.error(f"Error adding conversation entry: {e}")
            raise

    async def get_recent_history(self, limit: int = 5) -> list:
        """Get recent conversation history"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    SELECT user_message, assistant_message 
                    FROM conversation_history 
                    ORDER BY timestamp DESC LIMIT ?
                """, (limit,))
                
                history = []
                for user_msg, asst_msg in cursor.fetchall():
                    history.append({
                        'user': user_msg,
                        'assistant': asst_msg
                    })
                
                return list(reversed(history))  # Return in chronological order
        except Exception as e:
            logger.error(f"Error getting conversation history: {e}")
            return []
