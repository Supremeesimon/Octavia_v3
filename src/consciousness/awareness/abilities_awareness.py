"""
Octavia's Abilities Awareness System - Tracks and manages understanding of available capabilities
"""

from typing import Dict, List, Optional, Any, Set
from enum import Enum
from dataclasses import dataclass
from datetime import datetime
import json
from pathlib import Path
import sqlite3
from loguru import logger

class AbilityType(Enum):
    """Types of abilities Octavia can have"""
    PERCEPTION = "perception"       # Abilities to perceive and understand input
    COGNITION = "cognition"        # Abilities to process and reason
    ACTION = "action"              # Abilities to take action or make changes
    LEARNING = "learning"          # Abilities to learn and adapt
    COMMUNICATION = "communication" # Abilities to interact and express
    MEMORY = "memory"              # Abilities to store and recall information
    AWARENESS = "awareness"        # Meta-abilities for self-awareness
    UI = "ui"                      # UI-related abilities

class AbilityStatus(Enum):
    """Status of an ability"""
    ACTIVE = "active"           # Currently available and working
    INACTIVE = "inactive"       # Present but not currently available
    LEARNING = "learning"       # Still being developed/learned
    DEPRECATED = "deprecated"   # No longer in use
    SUCCESS = "success"         # Operation completed successfully
    FAILURE = "failure"         # Operation failed

@dataclass
class AbilityMetrics:
    """Metrics tracking ability usage and effectiveness"""
    usage_count: int = 0
    success_rate: float = 0.0
    avg_response_time: float = 0.0
    last_used: Optional[datetime] = None
    confidence_level: float = 0.5

class AbilityAwareness:
    """Manages awareness of Octavia's abilities"""
    
    def __init__(self, db_path: Optional[str] = None):
        """Initialize abilities awareness system"""
        if db_path is None:
            db_path = Path.home() / ".octavia" / "abilities.db"
        db_path.parent.mkdir(parents=True, exist_ok=True)
        self.db_path = db_path
        self._init_database()
        self._active_abilities: Dict[str, Dict[str, Any]] = {}
        self._ability_metrics: Dict[str, AbilityMetrics] = {}
        
    def _init_database(self):
        """Initialize the abilities database"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # Store abilities
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS abilities (
                    id TEXT PRIMARY KEY,
                    name TEXT,
                    description TEXT,
                    ability_type TEXT,
                    status TEXT,
                    requirements TEXT,
                    created_at TEXT,
                    updated_at TEXT,
                    metadata TEXT
                )
            """)
            
            # Store ability relationships
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS ability_relationships (
                    ability_id TEXT,
                    related_id TEXT,
                    relationship_type TEXT,
                    FOREIGN KEY(ability_id) REFERENCES abilities(id),
                    FOREIGN KEY(related_id) REFERENCES abilities(id)
                )
            """)
            
            # Store ability metrics
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS ability_metrics (
                    ability_id TEXT,
                    timestamp TEXT,
                    metric_type TEXT,
                    metric_value REAL,
                    FOREIGN KEY(ability_id) REFERENCES abilities(id)
                )
            """)
            
    async def register_ability(self, name: str, description: str,
                             ability_type: AbilityType,
                             handler: Optional[callable] = None,
                             requirements: Optional[Dict[str, Any]] = None,
                             metadata: Optional[Dict[str, Any]] = None) -> str:
        """Register a new ability"""
        try:
            ability_id = f"ability_{datetime.now().isoformat()}"
            now = datetime.now().isoformat()
            
            if metadata is None:
                metadata = {}
            if handler:
                metadata['handler'] = handler.__name__
            
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    INSERT INTO abilities
                    (id, name, description, ability_type, status, requirements,
                     created_at, updated_at, metadata)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    ability_id,
                    name,
                    description,
                    ability_type.value,
                    AbilityStatus.ACTIVE.value,
                    json.dumps(requirements or {}),
                    now,
                    now,
                    json.dumps(metadata)
                ))
                
            # Initialize metrics
            self._ability_metrics[ability_id] = AbilityMetrics()
            
            # Add to active abilities
            self._active_abilities[ability_id] = {
                'id': ability_id,
                'name': name,
                'type': ability_type,
                'status': AbilityStatus.ACTIVE,
                'handler': handler
            }
            
            return ability_id
            
        except Exception as e:
            logger.error(f"Error registering ability: {e}")
            return ""
            
    async def update_ability_status(self, ability_id: str,
                                  status: AbilityStatus,
                                  reason: Optional[str] = None):
        """Update status of an ability"""
        try:
            now = datetime.now().isoformat()
            metadata = {'status_change_reason': reason} if reason else {}
            
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    UPDATE abilities
                    SET status = ?, updated_at = ?, metadata = ?
                    WHERE id = ?
                """, (
                    status.value,
                    now,
                    json.dumps(metadata),
                    ability_id
                ))
                
            if ability_id in self._active_abilities:
                self._active_abilities[ability_id]['status'] = status
                
        except Exception as e:
            logger.error(f"Error updating ability status: {e}")
            
    async def record_ability_use(self, ability_id: str, success: bool,
                               response_time: float,
                               context: Optional[Dict[str, Any]] = None):
        """Record usage of an ability"""
        try:
            metrics = self._ability_metrics.get(ability_id)
            if not metrics:
                metrics = AbilityMetrics()
                self._ability_metrics[ability_id] = metrics
                
            # Update metrics
            metrics.usage_count += 1
            metrics.last_used = datetime.now()
            metrics.avg_response_time = (
                (metrics.avg_response_time * (metrics.usage_count - 1) + response_time)
                / metrics.usage_count
            )
            
            # Update success rate
            if success:
                metrics.success_rate = (
                    (metrics.success_rate * (metrics.usage_count - 1) + 1)
                    / metrics.usage_count
                )
            else:
                metrics.success_rate = (
                    metrics.success_rate * (metrics.usage_count - 1)
                    / metrics.usage_count
                )
                
            # Update confidence based on recent performance
            metrics.confidence_level = (
                0.7 * metrics.success_rate +
                0.3 * min(1.0, 1.0 / (metrics.avg_response_time + 1))
            )
            
            # Store metrics in database
            now = datetime.now().isoformat()
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                for metric_type, value in [
                    ('usage_count', metrics.usage_count),
                    ('success_rate', metrics.success_rate),
                    ('response_time', response_time),
                    ('confidence', metrics.confidence_level)
                ]:
                    cursor.execute("""
                        INSERT INTO ability_metrics
                        (ability_id, timestamp, metric_type, metric_value)
                        VALUES (?, ?, ?, ?)
                    """, (ability_id, now, metric_type, value))
                    
        except Exception as e:
            logger.error(f"Error recording ability use: {e}")
            
    async def get_ability_metrics(self, ability_id: str) -> Optional[AbilityMetrics]:
        """Get current metrics for an ability"""
        return self._ability_metrics.get(ability_id)
        
    async def find_relevant_abilities(self, context: Dict[str, Any],
                                    min_confidence: float = 0.5) -> List[Dict[str, Any]]:
        """Find abilities relevant to given context"""
        try:
            relevant_abilities = []
            
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    SELECT id, name, description, ability_type, status, metadata
                    FROM abilities
                    WHERE status = ?
                """, (AbilityStatus.ACTIVE.value,))
                
                for row in cursor.fetchall():
                    ability_id = row[0]
                    metrics = self._ability_metrics.get(ability_id)
                    
                    if metrics and metrics.confidence_level >= min_confidence:
                        metadata = json.loads(row[5])
                        relevance = self._calculate_ability_relevance(
                            context,
                            metadata.get('contexts', [])
                        )
                        
                        if relevance > 0.5:
                            relevant_abilities.append({
                                'id': ability_id,
                                'name': row[1],
                                'type': row[3],
                                'confidence': metrics.confidence_level,
                                'relevance': relevance
                            })
                            
            return sorted(
                relevant_abilities,
                key=lambda x: x['relevance'] * x['confidence'],
                reverse=True
            )
            
        except Exception as e:
            logger.error(f"Error finding relevant abilities: {e}")
            return []
            
    def _calculate_ability_relevance(self, current_context: Dict[str, Any],
                                   ability_contexts: List[Dict[str, Any]]) -> float:
        """Calculate relevance of ability to current context"""
        try:
            if not ability_contexts:
                return 0.5  # Default relevance for abilities without context
                
            max_relevance = 0.0
            for ability_context in ability_contexts:
                relevance = 0.0
                common_keys = set(current_context.keys()) & set(ability_context.keys())
                
                if not common_keys:
                    continue
                    
                for key in common_keys:
                    if isinstance(current_context[key], (str, int, float, bool)):
                        relevance += (
                            1.0 if current_context[key] == ability_context[key]
                            else 0.0
                        )
                    elif isinstance(current_context[key], (list, set)):
                        common = set(current_context[key]) & set(ability_context[key])
                        total = set(current_context[key]) | set(ability_context[key])
                        relevance += len(common) / len(total) if total else 0.0
                        
                relevance /= len(common_keys)
                max_relevance = max(max_relevance, relevance)
                
            return max_relevance
            
        except Exception as e:
            logger.error(f"Error calculating ability relevance: {e}")
            return 0.0
            
    async def get_ability_suggestions(self, context: Dict[str, Any],
                                    current_abilities: Set[str]) -> List[Dict[str, Any]]:
        """Get suggestions for new abilities based on context"""
        try:
            suggestions = []
            
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # Find abilities often used in similar contexts
                cursor.execute("""
                    SELECT a.id, a.name, a.description, a.ability_type,
                           COUNT(m.ability_id) as usage_count,
                           AVG(m.metric_value) as avg_success
                    FROM abilities a
                    JOIN ability_metrics m ON a.id = m.ability_id
                    WHERE a.id NOT IN ({})
                    AND m.metric_type = 'success_rate'
                    GROUP BY a.id
                    HAVING avg_success >= 0.7
                    ORDER BY usage_count DESC, avg_success DESC
                    LIMIT 5
                """.format(','.join(['?'] * len(current_abilities))),
                    tuple(current_abilities))
                
                for row in cursor.fetchall():
                    suggestions.append({
                        'id': row[0],
                        'name': row[1],
                        'description': row[2],
                        'type': row[3],
                        'confidence': row[5]
                    })
                    
            return suggestions
            
        except Exception as e:
            logger.error(f"Error getting ability suggestions: {e}")
            return []
