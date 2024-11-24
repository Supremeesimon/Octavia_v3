"""
Octavia's Task Awareness System - Manages and tracks tasks and their relationships
"""

from typing import Dict, List, Optional, Any, Set
from datetime import datetime, timedelta
from enum import Enum
import sqlite3
from pathlib import Path
import json
from loguru import logger

class TaskStatus(Enum):
    """Task status states"""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    BLOCKED = "blocked"
    COMPLETED = "completed"
    FAILED = "failed"

class TaskPriority(Enum):
    """Task priority levels"""
    LOW = 1
    MEDIUM = 2
    HIGH = 3
    CRITICAL = 4

class TaskAwareness:
    """Manages task awareness and relationships"""
    
    def __init__(self, db_path: Optional[str] = None):
        if db_path is None:
            db_path = Path.home() / ".octavia" / "tasks.db"
        db_path.parent.mkdir(parents=True, exist_ok=True)
        self.db_path = db_path
        self._init_database()
        self._active_tasks: Dict[str, Dict[str, Any]] = {}
        
    def _init_database(self):
        """Initialize the task database"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # Store tasks
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS tasks (
                    id TEXT PRIMARY KEY,
                    title TEXT,
                    description TEXT,
                    status TEXT,
                    priority TEXT,
                    created_at TEXT,
                    updated_at TEXT,
                    completed_at TEXT,
                    metadata TEXT
                )
            """)
            
            # Store task dependencies
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS task_dependencies (
                    task_id TEXT,
                    depends_on TEXT,
                    FOREIGN KEY(task_id) REFERENCES tasks(id),
                    FOREIGN KEY(depends_on) REFERENCES tasks(id)
                )
            """)
            
            # Store task context
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS task_context (
                    task_id TEXT,
                    context_type TEXT,
                    context_data TEXT,
                    FOREIGN KEY(task_id) REFERENCES tasks(id)
                )
            """)
            
    async def create_task(self, title: str, description: str,
                         priority: TaskPriority = TaskPriority.MEDIUM,
                         depends_on: Optional[List[str]] = None,
                         context: Optional[Dict[str, Any]] = None) -> str:
        """Create a new task"""
        try:
            task_id = f"task_{datetime.now().isoformat()}"
            now = datetime.now().isoformat()
            
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # Create task
                cursor.execute("""
                    INSERT INTO tasks
                    (id, title, description, status, priority, created_at, updated_at, metadata)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    task_id,
                    title,
                    description,
                    TaskStatus.PENDING.value,
                    priority.value,
                    now,
                    now,
                    "{}"
                ))
                
                # Add dependencies
                if depends_on:
                    for dep in depends_on:
                        cursor.execute("""
                            INSERT INTO task_dependencies
                            (task_id, depends_on)
                            VALUES (?, ?)
                        """, (task_id, dep))
                        
                # Add context
                if context:
                    for context_type, context_data in context.items():
                        cursor.execute("""
                            INSERT INTO task_context
                            (task_id, context_type, context_data)
                            VALUES (?, ?, ?)
                        """, (task_id, context_type, json.dumps(context_data)))
                        
            # Add to active tasks
            self._active_tasks[task_id] = {
                'id': task_id,
                'title': title,
                'status': TaskStatus.PENDING,
                'priority': priority,
                'context': context or {}
            }
            
            return task_id
            
        except Exception as e:
            logger.error(f"Error creating task: {e}")
            return ""
            
    async def update_task_status(self, task_id: str, 
                               status: TaskStatus,
                               metadata: Optional[Dict[str, Any]] = None):
        """Update task status"""
        try:
            now = datetime.now().isoformat()
            completed_at = now if status == TaskStatus.COMPLETED else None
            
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    UPDATE tasks
                    SET status = ?, updated_at = ?, completed_at = ?, metadata = ?
                    WHERE id = ?
                """, (
                    status.value,
                    now,
                    completed_at,
                    json.dumps(metadata or {}),
                    task_id
                ))
                
            if task_id in self._active_tasks:
                self._active_tasks[task_id]['status'] = status
                
        except Exception as e:
            logger.error(f"Error updating task: {e}")
            
    async def get_task_chain(self, task_id: str) -> List[Dict[str, Any]]:
        """Get task and its dependencies"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                def get_dependencies(tid: str, chain: Set[str]) -> List[Dict[str, Any]]:
                    if tid in chain:  # Prevent cycles
                        return []
                        
                    chain.add(tid)
                    cursor.execute("""
                        SELECT t.*, GROUP_CONCAT(tc.context_type || ':' || tc.context_data)
                        FROM tasks t
                        LEFT JOIN task_context tc ON t.id = tc.task_id
                        WHERE t.id = ?
                        GROUP BY t.id
                    """, (tid,))
                    
                    task_row = cursor.fetchone()
                    if not task_row:
                        return []
                        
                    task = {
                        'id': task_row[0],
                        'title': task_row[1],
                        'description': task_row[2],
                        'status': task_row[3],
                        'priority': task_row[4],
                        'created_at': task_row[5],
                        'context': self._parse_context(task_row[8]) if task_row[8] else {}
                    }
                    
                    # Get dependencies
                    cursor.execute("""
                        SELECT depends_on FROM task_dependencies WHERE task_id = ?
                    """, (tid,))
                    
                    deps = []
                    for dep_row in cursor.fetchall():
                        deps.extend(get_dependencies(dep_row[0], chain))
                        
                    return [task] + deps
                    
                return get_dependencies(task_id, set())
                
        except Exception as e:
            logger.error(f"Error getting task chain: {e}")
            return []
            
    def _parse_context(self, context_str: str) -> Dict[str, Any]:
        """Parse context string into dictionary"""
        try:
            if not context_str:
                return {}
                
            context = {}
            for item in context_str.split(','):
                if ':' in item:
                    type_str, data_str = item.split(':', 1)
                    context[type_str] = json.loads(data_str)
            return context
            
        except Exception as e:
            logger.error(f"Error parsing context: {e}")
            return {}
            
    async def get_related_tasks(self, context: Dict[str, Any],
                              limit: int = 5) -> List[Dict[str, Any]]:
        """Get tasks related to given context"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # Find tasks with similar context
                tasks = []
                for context_type, context_data in context.items():
                    cursor.execute("""
                        SELECT t.*, tc.context_data
                        FROM tasks t
                        JOIN task_context tc ON t.id = tc.task_id
                        WHERE tc.context_type = ?
                        AND t.status != ?
                        ORDER BY t.updated_at DESC
                        LIMIT ?
                    """, (context_type, TaskStatus.COMPLETED.value, limit))
                    
                    for row in cursor.fetchall():
                        task_context = json.loads(row[8]) if row[8] else {}
                        relevance = self._calculate_context_relevance(
                            context_data, json.loads(row[-1])
                        )
                        
                        if relevance > 0.5:
                            tasks.append({
                                'id': row[0],
                                'title': row[1],
                                'status': row[3],
                                'priority': row[4],
                                'relevance': relevance
                            })
                            
                return sorted(tasks, key=lambda x: x['relevance'], reverse=True)[:limit]
                
        except Exception as e:
            logger.error(f"Error getting related tasks: {e}")
            return []
            
    def _calculate_context_relevance(self, context1: Any, context2: Any) -> float:
        """Calculate relevance between two context values"""
        try:
            if isinstance(context1, (str, int, float, bool)):
                return 1.0 if context1 == context2 else 0.0
            elif isinstance(context1, (list, set)):
                common = set(context1) & set(context2)
                total = set(context1) | set(context2)
                return len(common) / len(total) if total else 0.0
            elif isinstance(context1, dict):
                relevance = 0.0
                common_keys = set(context1.keys()) & set(context2.keys())
                if not common_keys:
                    return 0.0
                for key in common_keys:
                    relevance += self._calculate_context_relevance(
                        context1[key], context2[key]
                    )
                return relevance / len(common_keys)
            return 0.0
            
        except Exception as e:
            logger.error(f"Error calculating relevance: {e}")
            return 0.0
