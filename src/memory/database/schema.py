"""
Database schema for Octavia's memory system.
Defines the structure of our SQLite database.
"""

SCHEMA_VERSION = 1

# SQL statements for creating tables
SCHEMA_CREATION = [
    """
    CREATE TABLE IF NOT EXISTS conversations (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
        user_message TEXT NOT NULL,
        octavia_response TEXT NOT NULL,
        context_data TEXT,  -- JSON string for flexible context storage
        conversation_id TEXT  -- Group related messages
    );
    """,
    """
    CREATE TABLE IF NOT EXISTS command_history (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
        command TEXT NOT NULL,
        shell_type TEXT NOT NULL,  -- 'powershell' or 'cmd'
        success BOOLEAN NOT NULL,
        error_message TEXT,
        context_data TEXT  -- JSON string for additional data
    );
    """,
    """
    CREATE TABLE IF NOT EXISTS preferences (
        key TEXT PRIMARY KEY,
        value TEXT NOT NULL,
        last_updated DATETIME DEFAULT CURRENT_TIMESTAMP
    );
    """,
    """
    CREATE TABLE IF NOT EXISTS learned_patterns (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        pattern_type TEXT NOT NULL,  -- 'command', 'conversation', etc.
        pattern_data TEXT NOT NULL,  -- JSON string of the pattern
        success_rate REAL DEFAULT 0.0,
        usage_count INTEGER DEFAULT 0,
        last_used DATETIME DEFAULT CURRENT_TIMESTAMP
    );
    """
]

# Default preferences
DEFAULT_PREFERENCES = {
    'default_shell': 'powershell',
    'show_command_preview': 'true',
    'save_history': 'true',
    'max_history_age_days': '30'
}
