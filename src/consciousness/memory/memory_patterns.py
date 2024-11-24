"""
Octavia's Memory Pattern System - Tracks and learns from user interaction patterns
"""

from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
import sqlite3
from pathlib import Path
import json
from loguru import logger

class MemoryPatterns:
    """Manages and learns from user interaction patterns"""
    
    def __init__(self, db_path: Optional[str] = None):
        if db_path is None:
            db_path = Path.home() / ".octavia" / "memory.db"
        db_path.parent.mkdir(parents=True, exist_ok=True)
        self.db_path = db_path
        self._init_database()
        
    def _init_database(self):
        """Initialize the memory database"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # Store interaction patterns
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS interaction_patterns (
                    id INTEGER PRIMARY KEY,
                    pattern_type TEXT,
                    pattern_data TEXT,
                    frequency INTEGER,
                    last_used TIMESTAMP,
                    success_rate REAL
                )
            """)
            
            # Store file access patterns
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS file_patterns (
                    id INTEGER PRIMARY KEY,
                    file_path TEXT,
                    access_count INTEGER,
                    last_access TIMESTAMP,
                    context TEXT
                )
            """)
            
            # Store task patterns
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS task_patterns (
                    id INTEGER PRIMARY KEY,
                    task_type TEXT,
                    task_data TEXT,
                    completion_time INTEGER,
                    success_rate REAL,
                    last_performed TIMESTAMP
                )
            """)
            
    async def record_interaction(self, pattern_type: str, pattern_data: Dict[str, Any], success: bool = True):
        """Record a new interaction pattern"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # Check if pattern exists
                cursor.execute("""
                    SELECT id, frequency, success_rate FROM interaction_patterns
                    WHERE pattern_type = ? AND pattern_data = ?
                """, (pattern_type, json.dumps(pattern_data)))
                
                result = cursor.fetchone()
                
                if result:
                    # Update existing pattern
                    pattern_id, frequency, success_rate = result
                    new_frequency = frequency + 1
                    new_success_rate = (success_rate * frequency + (1 if success else 0)) / new_frequency
                    
                    cursor.execute("""
                        UPDATE interaction_patterns
                        SET frequency = ?, success_rate = ?, last_used = CURRENT_TIMESTAMP
                        WHERE id = ?
                    """, (new_frequency, new_success_rate, pattern_id))
                else:
                    # Insert new pattern
                    cursor.execute("""
                        INSERT INTO interaction_patterns
                        (pattern_type, pattern_data, frequency, last_used, success_rate)
                        VALUES (?, ?, 1, CURRENT_TIMESTAMP, ?)
                    """, (pattern_type, json.dumps(pattern_data), 1.0 if success else 0.0))
                    
        except Exception as e:
            logger.error(f"Error recording interaction pattern: {e}")
            
    async def get_relevant_patterns(self, pattern_type: str, context: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Get patterns relevant to current context"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # Get recent successful patterns
                cursor.execute("""
                    SELECT pattern_data, frequency, success_rate
                    FROM interaction_patterns
                    WHERE pattern_type = ?
                    AND success_rate > 0.7
                    AND last_used > datetime('now', '-7 days')
                    ORDER BY frequency * success_rate DESC
                    LIMIT 5
                """, (pattern_type,))
                
                patterns = []
                for row in cursor.fetchall():
                    pattern_data = json.loads(row[0])
                    relevance = self._calculate_relevance(pattern_data, context)
                    if relevance > 0.5:
                        patterns.append({
                            'pattern': pattern_data,
                            'frequency': row[1],
                            'success_rate': row[2],
                            'relevance': relevance
                        })
                
                return sorted(patterns, key=lambda x: x['relevance'], reverse=True)
                
        except Exception as e:
            logger.error(f"Error retrieving patterns: {e}")
            return []
            
    def _calculate_relevance(self, pattern: Dict[str, Any], context: Dict[str, Any]) -> float:
        """Calculate pattern relevance to current context"""
        relevance = 0.0
        total_weights = 0.0
        
        # Compare common keys
        for key in set(pattern.keys()) & set(context.keys()):
            weight = self._get_key_weight(key)
            if isinstance(pattern[key], (str, int, float, bool)):
                relevance += weight * (1.0 if pattern[key] == context[key] else 0.0)
            elif isinstance(pattern[key], (list, set)):
                common = set(pattern[key]) & set(context.get(key, []))
                total = set(pattern[key]) | set(context.get(key, []))
                relevance += weight * (len(common) / len(total) if total else 0.0)
            total_weights += weight
            
        return relevance / total_weights if total_weights > 0 else 0.0
        
    def _get_key_weight(self, key: str) -> float:
        """Get weight for context key"""
        weights = {
            'task_type': 1.0,
            'file_type': 0.8,
            'command': 0.8,
            'directory': 0.6,
            'tags': 0.4
        }
        return weights.get(key, 0.5)


class MemoryPatternTracker:
    """High-level interface for tracking and analyzing memory patterns"""
    
    def __init__(self, db_path: Optional[str] = None):
        """Initialize the memory pattern tracker"""
        self.patterns = MemoryPatterns(db_path)
        
    async def track_interaction(self, pattern_type: str, pattern_data: Dict[str, Any], success: bool = True):
        """Track a new interaction pattern"""
        await self.patterns.record_interaction(pattern_type, pattern_data, success)
        
    async def get_relevant_patterns(self, pattern_type: str, context: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Get patterns relevant to current context"""
        return await self.patterns.get_relevant_patterns(pattern_type, context)
        
    def calculate_relevance(self, pattern: Dict[str, Any], context: Dict[str, Any]) -> float:
        """Calculate pattern relevance to current context"""
        return self.patterns._calculate_relevance(pattern, context)
