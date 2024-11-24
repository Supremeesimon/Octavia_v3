"""
Octavia's Context Continuity System - Maintains persistent awareness across sessions
"""

from typing import Dict, List, Optional, Any, Set
from datetime import datetime, timedelta
import sqlite3
from pathlib import Path
import json
from loguru import logger

class ContextNode:
    """Represents a single context node in the context graph"""
    def __init__(self, context_type: str, content: Dict[str, Any]):
        self.context_type = context_type
        self.content = content
        self.timestamp = datetime.now()
        self.references: Set[str] = set()  # IDs of related contexts
        self.importance = 1.0  # Dynamic importance score
        
    def to_dict(self) -> Dict[str, Any]:
        """Convert node to dictionary for storage"""
        return {
            'type': self.context_type,
            'content': self.content,
            'timestamp': self.timestamp.isoformat(),
            'references': list(self.references),
            'importance': self.importance
        }
        
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'ContextNode':
        """Create node from dictionary"""
        node = cls(data['type'], data['content'])
        node.timestamp = datetime.fromisoformat(data['timestamp'])
        node.references = set(data['references'])
        node.importance = data['importance']
        return node

class ContextContinuity:
    """Manages persistent context awareness"""
    
    def __init__(self, db_path: Optional[str] = None):
        if db_path is None:
            db_path = Path.home() / ".octavia" / "context.db"
        db_path.parent.mkdir(parents=True, exist_ok=True)
        self.db_path = db_path
        self._init_database()
        self._active_contexts: Dict[str, ContextNode] = {}
        
    def _init_database(self):
        """Initialize the context database"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # Store context nodes
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS context_nodes (
                    id TEXT PRIMARY KEY,
                    node_type TEXT,
                    content TEXT,
                    timestamp TEXT,
                    importance REAL
                )
            """)
            
            # Store context relationships
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS context_relations (
                    source_id TEXT,
                    target_id TEXT,
                    relation_type TEXT,
                    strength REAL,
                    FOREIGN KEY(source_id) REFERENCES context_nodes(id),
                    FOREIGN KEY(target_id) REFERENCES context_nodes(id)
                )
            """)
            
    async def add_context(self, context_type: str, content: Dict[str, Any], 
                         related_to: Optional[List[str]] = None) -> str:
        """Add new context node"""
        try:
            # Create new context node
            node = ContextNode(context_type, content)
            node_id = f"{context_type}_{datetime.now().isoformat()}"
            
            # Add references if provided
            if related_to:
                node.references.update(related_to)
            
            # Store in database
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    INSERT INTO context_nodes
                    (id, node_type, content, timestamp, importance)
                    VALUES (?, ?, ?, ?, ?)
                """, (
                    node_id,
                    node.context_type,
                    json.dumps(node.content),
                    node.timestamp.isoformat(),
                    node.importance
                ))
                
                # Store relations
                for ref in node.references:
                    cursor.execute("""
                        INSERT INTO context_relations
                        (source_id, target_id, relation_type, strength)
                        VALUES (?, ?, 'reference', 1.0)
                    """, (node_id, ref))
                    
            # Add to active contexts
            self._active_contexts[node_id] = node
            return node_id
            
        except Exception as e:
            logger.error(f"Error adding context: {e}")
            return ""
            
    async def get_relevant_contexts(self, context_type: Optional[str] = None,
                                  timeframe: Optional[timedelta] = None,
                                  limit: int = 5) -> List[Dict[str, Any]]:
        """Get relevant context nodes"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                query = """
                    SELECT id, node_type, content, timestamp, importance
                    FROM context_nodes
                    WHERE 1=1
                """
                params = []
                
                if context_type:
                    query += " AND node_type = ?"
                    params.append(context_type)
                    
                if timeframe:
                    min_time = (datetime.now() - timeframe).isoformat()
                    query += " AND timestamp > ?"
                    params.append(min_time)
                    
                query += " ORDER BY importance DESC LIMIT ?"
                params.append(limit)
                
                cursor.execute(query, params)
                contexts = []
                
                for row in cursor.fetchall():
                    node = {
                        'id': row[0],
                        'type': row[1],
                        'content': json.loads(row[2]),
                        'timestamp': datetime.fromisoformat(row[3]),
                        'importance': row[4]
                    }
                    contexts.append(node)
                    
                return contexts
                
        except Exception as e:
            logger.error(f"Error retrieving contexts: {e}")
            return []
            
    async def update_importance(self, context_id: str, factor: float):
        """Update context importance"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    UPDATE context_nodes
                    SET importance = importance * ?
                    WHERE id = ?
                """, (factor, context_id))
                
            if context_id in self._active_contexts:
                self._active_contexts[context_id].importance *= factor
                
        except Exception as e:
            logger.error(f"Error updating context importance: {e}")
            
    async def prune_old_contexts(self, max_age: timedelta):
        """Remove old, low-importance contexts"""
        try:
            min_time = (datetime.now() - max_age).isoformat()
            
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    DELETE FROM context_relations
                    WHERE source_id IN (
                        SELECT id FROM context_nodes
                        WHERE timestamp < ?
                        AND importance < 0.5
                    )
                """, (min_time,))
                
                cursor.execute("""
                    DELETE FROM context_nodes
                    WHERE timestamp < ?
                    AND importance < 0.5
                """, (min_time,))
                
        except Exception as e:
            logger.error(f"Error pruning contexts: {e}")
            
    def get_active_context_summary(self) -> Dict[str, Any]:
        """Get summary of current active contexts"""
        summary = {
            'types': {},
            'recent_topics': [],
            'important_contexts': []
        }
        
        for node in self._active_contexts.values():
            # Count context types
            if node.context_type not in summary['types']:
                summary['types'][node.context_type] = 0
            summary['types'][node.context_type] += 1
            
            # Track recent topics
            if len(summary['recent_topics']) < 5:
                summary['recent_topics'].append(node.content.get('topic', ''))
                
            # Track important contexts
            if node.importance > 0.8:
                summary['important_contexts'].append({
                    'type': node.context_type,
                    'content': node.content
                })
                
        return summary

class ContextContinuityManager:
    """High-level interface for managing context continuity"""
    
    def __init__(self, db_path: Optional[str] = None):
        """Initialize the context continuity manager"""
        self.context = ContextContinuity(db_path)
        
    async def add_context(self, context_type: str, content: Dict[str, Any]) -> str:
        """Add a new context node"""
        return await self.context.add_context(context_type, content)
        
    async def get_context(self, context_id: str) -> Optional[Dict[str, Any]]:
        """Get context by ID"""
        try:
            with sqlite3.connect(self.context.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    SELECT node_type, content, timestamp, importance
                    FROM context_nodes
                    WHERE id = ?
                """, (context_id,))
                
                result = cursor.fetchone()
                if result:
                    return {
                        'id': context_id,
                        'type': result[0],
                        'content': json.loads(result[1]),
                        'timestamp': result[2],
                        'importance': result[3]
                    }
                return None
                
        except Exception as e:
            logger.error(f"Error getting context: {e}")
            return None
        
    async def update_context(self, context_id: str, content: Dict[str, Any]) -> bool:
        """Update existing context"""
        try:
            with sqlite3.connect(self.context.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    UPDATE context_nodes
                    SET content = ?, timestamp = ?
                    WHERE id = ?
                """, (json.dumps(content), datetime.now().isoformat(), context_id))
                return cursor.rowcount > 0
                
        except Exception as e:
            logger.error(f"Error updating context: {e}")
            return False
        
    async def add_reference(self, source_id: str, target_id: str) -> bool:
        """Add reference between contexts"""
        try:
            with sqlite3.connect(self.context.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    INSERT INTO context_relations
                    (source_id, target_id, relation_type, strength)
                    VALUES (?, ?, 'reference', 1.0)
                """, (source_id, target_id))
                return True
                
        except Exception as e:
            logger.error(f"Error adding reference: {e}")
            return False
        
    async def get_related_contexts(self, context_id: str) -> List[Dict[str, Any]]:
        """Get contexts related to given context"""
        try:
            with sqlite3.connect(self.context.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    SELECT n.id, n.node_type, n.content, n.timestamp, n.importance, r.strength
                    FROM context_nodes n
                    JOIN context_relations r ON n.id = r.target_id
                    WHERE r.source_id = ?
                    ORDER BY r.strength DESC
                """, (context_id,))
                
                contexts = []
                for row in cursor.fetchall():
                    contexts.append({
                        'id': row[0],
                        'type': row[1],
                        'content': json.loads(row[2]),
                        'timestamp': row[3],
                        'importance': row[4],
                        'relation_strength': row[5]
                    })
                return contexts
                
        except Exception as e:
            logger.error(f"Error getting related contexts: {e}")
            return []
        
    async def prune_old_contexts(self, days: int = 30) -> int:
        """Remove contexts older than specified days"""
        try:
            cutoff = (datetime.now() - timedelta(days=days)).isoformat()
            with sqlite3.connect(self.context.db_path) as conn:
                cursor = conn.cursor()
                
                # Delete relations first
                cursor.execute("""
                    DELETE FROM context_relations
                    WHERE source_id IN (
                        SELECT id FROM context_nodes
                        WHERE timestamp < ?
                    ) OR target_id IN (
                        SELECT id FROM context_nodes
                        WHERE timestamp < ?
                    )
                """, (cutoff, cutoff))
                
                # Then delete nodes
                cursor.execute("""
                    DELETE FROM context_nodes
                    WHERE timestamp < ?
                """, (cutoff,))
                
                return cursor.rowcount
                
        except Exception as e:
            logger.error(f"Error pruning contexts: {e}")
            return 0
        
    def get_active_contexts(self) -> List[Dict[str, Any]]:
        """Get currently active contexts"""
        active = []
        for context_id, node in self.context._active_contexts.items():
            active.append({
                'id': context_id,
                'type': node.context_type,
                'content': node.content,
                'timestamp': node.timestamp.isoformat(),
                'importance': node.importance
            })
        return active
