"""
Octavia's Context Management System
"""

import json
import sqlite3
from typing import Dict, List, Optional
from datetime import datetime
from pathlib import Path
from loguru import logger
from sklearn.feature_extraction.text import TfidfVectorizer
import numpy as np

class ContextManager:
    """Manages Octavia's understanding of context and state"""
    
    def __init__(self, db_path: Optional[str] = None, use_temp: bool = False):
        """Initialize context manager with database connection
        
        Args:
            db_path: Optional path to database file
            use_temp: If True, use an in-memory SQLite database for testing
        """
        if use_temp:
            self.db_path = ":memory:"
            logger.info("Using in-memory database for testing")
        else:
            if db_path is None:
                db_path = Path.home() / ".octavia" / "context.db"
            
            # Ensure directory exists
            db_path.parent.mkdir(parents=True, exist_ok=True)
            self.db_path = db_path
            logger.info(f"Initialized Context Manager with database at {db_path}")

        self._init_database()

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
                    CREATE TABLE IF NOT EXISTS conversation_summaries (
                        id INTEGER PRIMARY KEY,
                        timestamp TEXT,
                        importance REAL,
                        topics TEXT,
                        key_points TEXT,
                        messages TEXT,
                        embedding TEXT
                    )
                """)
                
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS topic_relationships (
                        id INTEGER PRIMARY KEY,
                        topic_a TEXT,
                        topic_b TEXT,
                        strength REAL,
                        last_updated TEXT
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
                
                logger.info("Database tables initialized successfully")
                
        except Exception as e:
            logger.error(f"Error initializing database: {e}")
            raise
            
    def store_conversation_summaries(self, summaries: List[Dict]):
        """Store conversation summaries with embeddings"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                for summary in summaries:
                    # Create embedding for efficient similarity search
                    embedding = self._create_embedding(" ".join(summary['messages']))
                    
                    cursor.execute("""
                        INSERT INTO conversation_summaries
                        (timestamp, importance, topics, key_points, messages, embedding)
                        VALUES (?, ?, ?, ?, ?, ?)
                    """, (
                        summary['timestamp'],
                        summary['importance'],
                        json.dumps(summary['topics']),
                        json.dumps(summary['key_points']),
                        json.dumps(summary['messages']),
                        json.dumps(embedding.tolist() if embedding is not None else [])
                    ))
                    
                    # Update topic relationships
                    self._update_topic_relationships(cursor, summary['topics'])
                    
                conn.commit()
                logger.info(f"Stored {len(summaries)} conversation summaries")
                
        except Exception as e:
            logger.error(f"Error storing conversation summaries: {e}")
            
    def get_relevant_summaries(self, current_topic: str, limit: int = 5) -> List[Dict]:
        """Retrieve relevant conversation summaries based on topic similarity"""
        try:
            current_embedding = self._create_embedding(current_topic)
            if current_embedding is None:
                return []
                
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # Get all summaries
                cursor.execute("SELECT * FROM conversation_summaries ORDER BY timestamp DESC")
                summaries = cursor.fetchall()
                
                # Calculate relevance scores
                scored_summaries = []
                for summary in summaries:
                    embedding = np.array(json.loads(summary[6]))  # embedding column
                    if len(embedding) > 0:
                        similarity = np.dot(current_embedding, embedding) / (
                            np.linalg.norm(current_embedding) * np.linalg.norm(embedding)
                        )
                        scored_summaries.append((summary, similarity))
                
                # Sort by relevance and return top matches
                scored_summaries.sort(key=lambda x: x[1], reverse=True)
                return [
                    {
                        'timestamp': s[1],
                        'importance': s[2],
                        'topics': json.loads(s[3]),
                        'key_points': json.loads(s[4]),
                        'messages': json.loads(s[5])
                    }
                    for s, _ in scored_summaries[:limit]
                ]
                
        except Exception as e:
            logger.error(f"Error retrieving relevant summaries: {e}")
            return []
            
    def _create_embedding(self, text: str) -> Optional[np.ndarray]:
        """Create a vector embedding for text"""
        try:
            vectorizer = TfidfVectorizer(max_features=100)
            tfidf_matrix = vectorizer.fit_transform([text])
            return tfidf_matrix.toarray()[0]
        except:
            return None
            
    def _update_topic_relationships(self, cursor, topics: List[str]):
        """Update relationships between topics"""
        timestamp = datetime.now().isoformat()
        
        for i, topic_a in enumerate(topics):
            for topic_b in topics[i+1:]:
                cursor.execute("""
                    INSERT INTO topic_relationships (topic_a, topic_b, strength, last_updated)
                    VALUES (?, ?, 1, ?)
                    ON CONFLICT (topic_a, topic_b) DO UPDATE SET
                    strength = strength + 1,
                    last_updated = ?
                """, (topic_a, topic_b, timestamp, timestamp))
                
    def clear_conversation_summaries(self):
        """Clear all stored conversation summaries"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("DELETE FROM conversation_summaries")
                cursor.execute("DELETE FROM topic_relationships")
                conn.commit()
                logger.info("Cleared all conversation summaries")
        except Exception as e:
            logger.error(f"Error clearing summaries: {e}")

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
