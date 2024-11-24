"""
Octavia's Learning Adaptation System - Evolves interaction style based on feedback
"""

from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime, timedelta
import sqlite3
from pathlib import Path
import json
from loguru import logger
import numpy as np
from dataclasses import dataclass

@dataclass
class InteractionStyle:
    """Represents user's preferred interaction style"""
    technical_level: float = 0.5  # 0=basic, 1=expert
    verbosity: float = 0.5       # 0=concise, 1=detailed
    formality: float = 0.5       # 0=casual, 1=formal
    proactivity: float = 0.5     # 0=reactive, 1=proactive
    
    def to_dict(self) -> Dict[str, float]:
        """Convert to dictionary"""
        return {
            'technical_level': self.technical_level,
            'verbosity': self.verbosity,
            'formality': self.formality,
            'proactivity': self.proactivity
        }
        
    @classmethod
    def from_dict(cls, data: Dict[str, float]) -> 'InteractionStyle':
        """Create from dictionary"""
        return cls(
            technical_level=data.get('technical_level', 0.5),
            verbosity=data.get('verbosity', 0.5),
            formality=data.get('formality', 0.5),
            proactivity=data.get('proactivity', 0.5)
        )

class LearningAdaptation:
    """Manages learning and adaptation of interaction style"""
    
    def __init__(self, db_path: Optional[str] = None):
        if db_path is None:
            db_path = Path.home() / ".octavia" / "learning.db"
        db_path.parent.mkdir(parents=True, exist_ok=True)
        self.db_path = db_path
        self._init_database()
        self.current_style = InteractionStyle()
        self._load_style()
        
    def _init_database(self):
        """Initialize the learning database"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # Store interaction feedback
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS interaction_feedback (
                    id INTEGER PRIMARY KEY,
                    timestamp TEXT,
                    interaction_type TEXT,
                    content TEXT,
                    feedback_type TEXT,
                    feedback_value REAL
                )
            """)
            
            # Store learned preferences
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS learned_preferences (
                    preference_type TEXT PRIMARY KEY,
                    value REAL,
                    confidence REAL,
                    last_updated TEXT
                )
            """)
            
    def _load_style(self):
        """Load saved interaction style"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    SELECT preference_type, value
                    FROM learned_preferences
                """)
                
                preferences = {}
                for row in cursor.fetchall():
                    preferences[row[0]] = row[1]
                    
                if preferences:
                    self.current_style = InteractionStyle.from_dict(preferences)
                    
        except Exception as e:
            logger.error(f"Error loading style: {e}")
            
    async def record_feedback(self, interaction_type: str, 
                            content: Dict[str, Any],
                            feedback_type: str,
                            feedback_value: float):
        """Record user feedback"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    INSERT INTO interaction_feedback
                    (timestamp, interaction_type, content, feedback_type, feedback_value)
                    VALUES (?, ?, ?, ?, ?)
                """, (
                    datetime.now().isoformat(),
                    interaction_type,
                    json.dumps(content),
                    feedback_type,
                    feedback_value
                ))
                
            # Update style based on feedback
            await self._update_style(feedback_type, feedback_value)
            
        except Exception as e:
            logger.error(f"Error recording feedback: {e}")
            
    async def _update_style(self, feedback_type: str, value: float):
        """Update interaction style based on feedback"""
        try:
            # Map feedback types to style attributes
            style_updates = {
                'complexity': ('technical_level', value),
                'detail': ('verbosity', value),
                'tone': ('formality', value),
                'helpfulness': ('proactivity', value)
            }
            
            if feedback_type in style_updates:
                attr, val = style_updates[feedback_type]
                current = getattr(self.current_style, attr)
                # Smooth update
                new_val = current * 0.8 + val * 0.2
                setattr(self.current_style, attr, new_val)
                
                # Save to database
                with sqlite3.connect(self.db_path) as conn:
                    cursor = conn.cursor()
                    cursor.execute("""
                        INSERT OR REPLACE INTO learned_preferences
                        (preference_type, value, confidence, last_updated)
                        VALUES (?, ?, ?, ?)
                    """, (
                        attr,
                        new_val,
                        min(self._calculate_confidence(attr), 1.0),
                        datetime.now().isoformat()
                    ))
                    
        except Exception as e:
            logger.error(f"Error updating style: {e}")
            
    def _calculate_confidence(self, preference_type: str) -> float:
        """Calculate confidence in learned preference"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # Get recent feedback consistency
                week_ago = (datetime.now() - timedelta(days=7)).isoformat()
                cursor.execute("""
                    SELECT feedback_value
                    FROM interaction_feedback
                    WHERE feedback_type = ?
                    AND timestamp > ?
                """, (preference_type, week_ago))
                
                values = [row[0] for row in cursor.fetchall()]
                if not values:
                    return 0.5
                    
                # Calculate confidence based on consistency
                std_dev = np.std(values) if len(values) > 1 else 1.0
                return 1.0 / (1.0 + std_dev)
                
        except Exception as e:
            logger.error(f"Error calculating confidence: {e}")
            return 0.5
            
    async def analyze_feedback_patterns(self) -> Dict[str, Any]:
        """Analyze patterns in user feedback"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                patterns = {
                    'common_feedback': [],
                    'trend': {},
                    'confidence': {}
                }
                
                # Get most common feedback types
                cursor.execute("""
                    SELECT feedback_type, AVG(feedback_value)
                    FROM interaction_feedback
                    GROUP BY feedback_type
                    ORDER BY COUNT(*) DESC
                    LIMIT 3
                """)
                
                patterns['common_feedback'] = [
                    {'type': row[0], 'avg_value': row[1]}
                    for row in cursor.fetchall()
                ]
                
                # Calculate trends
                week_ago = (datetime.now() - timedelta(days=7)).isoformat()
                for feedback_type in ['complexity', 'detail', 'tone', 'helpfulness']:
                    cursor.execute("""
                        SELECT AVG(feedback_value)
                        FROM interaction_feedback
                        WHERE feedback_type = ?
                        AND timestamp > ?
                    """, (feedback_type, week_ago))
                    
                    row = cursor.fetchone()
                    if row and row[0]:
                        patterns['trend'][feedback_type] = row[0]
                        patterns['confidence'][feedback_type] = self._calculate_confidence(feedback_type)
                        
                return patterns
                
        except Exception as e:
            logger.error(f"Error analyzing feedback: {e}")
            return {}
