"""
Database manager for Octavia's memory system.
Handles all database operations with proper error handling and connection management.
"""

import sqlite3
import json
import os
from datetime import datetime
from pathlib import Path
from typing import Optional, Dict, List, Any, Union
from .schema import SCHEMA_CREATION, DEFAULT_PREFERENCES

class DatabaseManager:
    def __init__(self):
        # Create .octavia directory in user's home directory
        self.db_dir = Path.home() / '.octavia'
        self.db_dir.mkdir(exist_ok=True)
        self.db_path = self.db_dir / 'memory.db'
        self.setup_database()

    def setup_database(self):
        """Initialize the database with our schema."""
        with sqlite3.connect(self.db_path) as conn:
            for statement in SCHEMA_CREATION:
                conn.execute(statement)
            
            # Initialize default preferences if they don't exist
            for key, value in DEFAULT_PREFERENCES.items():
                conn.execute(
                    "INSERT OR IGNORE INTO preferences (key, value) VALUES (?, ?)",
                    (key, value)
                )
            conn.commit()

    def _get_connection(self) -> sqlite3.Connection:
        """Get a database connection with row factory."""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn

    # CRUD Operations for Conversations
    def save_conversation(self, user_message: str, octavia_response: str, 
                        context_data: Optional[Dict] = None, 
                        conversation_id: Optional[str] = None) -> int:
        """Save a conversation exchange."""
        with self._get_connection() as conn:
            cursor = conn.execute(
                """
                INSERT INTO conversations 
                (user_message, octavia_response, context_data, conversation_id)
                VALUES (?, ?, ?, ?)
                """,
                (user_message, octavia_response, 
                 json.dumps(context_data) if context_data else None,
                 conversation_id)
            )
            return cursor.lastrowid

    def get_recent_conversations(self, limit: int = 10) -> List[Dict]:
        """Get recent conversations."""
        with self._get_connection() as conn:
            cursor = conn.execute(
                """
                SELECT * FROM conversations 
                ORDER BY timestamp DESC LIMIT ?
                """, 
                (limit,)
            )
            return [dict(row) for row in cursor.fetchall()]

    # CRUD Operations for Command History
    def save_command(self, command: str, shell_type: str, success: bool, 
                    error_message: Optional[str] = None,
                    context_data: Optional[Dict] = None) -> int:
        """Save a command execution record."""
        with self._get_connection() as conn:
            cursor = conn.execute(
                """
                INSERT INTO command_history 
                (command, shell_type, success, error_message, context_data)
                VALUES (?, ?, ?, ?, ?)
                """,
                (command, shell_type, success, error_message,
                 json.dumps(context_data) if context_data else None)
            )
            return cursor.lastrowid

    def get_command_history(self, limit: int = 50) -> List[Dict]:
        """Get command execution history."""
        with self._get_connection() as conn:
            cursor = conn.execute(
                """
                SELECT * FROM command_history 
                ORDER BY timestamp DESC LIMIT ?
                """, 
                (limit,)
            )
            return [dict(row) for row in cursor.fetchall()]

    # CRUD Operations for Preferences
    def get_preference(self, key: str) -> Optional[str]:
        """Get a preference value."""
        with self._get_connection() as conn:
            cursor = conn.execute(
                "SELECT value FROM preferences WHERE key = ?",
                (key,)
            )
            result = cursor.fetchone()
            return result['value'] if result else None

    def set_preference(self, key: str, value: str):
        """Set a preference value."""
        with self._get_connection() as conn:
            conn.execute(
                """
                INSERT OR REPLACE INTO preferences (key, value, last_updated)
                VALUES (?, ?, CURRENT_TIMESTAMP)
                """,
                (key, value)
            )
            conn.commit()

    # CRUD Operations for Learned Patterns
    def save_pattern(self, pattern_type: str, pattern_data: Dict,
                    success_rate: float = 0.0) -> int:
        """Save a learned pattern."""
        with self._get_connection() as conn:
            cursor = conn.execute(
                """
                INSERT INTO learned_patterns 
                (pattern_type, pattern_data, success_rate)
                VALUES (?, ?, ?)
                """,
                (pattern_type, json.dumps(pattern_data), success_rate)
            )
            return cursor.lastrowid

    def get_patterns_by_type(self, pattern_type: str) -> List[Dict]:
        """Get learned patterns of a specific type."""
        with self._get_connection() as conn:
            cursor = conn.execute(
                """
                SELECT * FROM learned_patterns 
                WHERE pattern_type = ?
                ORDER BY success_rate DESC
                """,
                (pattern_type,)
            )
            return [dict(row) for row in cursor.fetchall()]

    def update_pattern_success_rate(self, pattern_id: int, success: bool):
        """Update success rate of a pattern."""
        with self._get_connection() as conn:
            # Get current stats
            cursor = conn.execute(
                """
                SELECT success_rate, usage_count 
                FROM learned_patterns 
                WHERE id = ?
                """,
                (pattern_id,)
            )
            result = cursor.fetchone()
            if result:
                current_rate = result['success_rate']
                usage_count = result['usage_count']
                
                # Calculate new success rate
                new_count = usage_count + 1
                new_rate = ((current_rate * usage_count) + (1 if success else 0)) / new_count
                
                # Update pattern
                conn.execute(
                    """
                    UPDATE learned_patterns 
                    SET success_rate = ?,
                        usage_count = ?,
                        last_used = CURRENT_TIMESTAMP
                    WHERE id = ?
                    """,
                    (new_rate, new_count, pattern_id)
                )
                conn.commit()
