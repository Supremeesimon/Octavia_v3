"""
Handles database migrations for Octavia's memory system.
"""

import json
import sqlite3
import shutil
from datetime import datetime
from pathlib import Path
from typing import List, Dict

class MigrationManager:
    def __init__(self, db_path: Path):
        self.db_path = db_path
        self.migrations_dir = db_path.parent / "migrations"
        self.migrations_dir.mkdir(exist_ok=True)
        self.version_file = self.migrations_dir / "version.json"
        self._init_version_control()

    def _init_version_control(self):
        """Initialize version control if it doesn't exist."""
        if not self.version_file.exists():
            version_data = {
                "current_version": 1,
                "last_migration": datetime.now().isoformat(),
                "migrations": []
            }
            self._save_version_data(version_data)

    def _save_version_data(self, data: Dict):
        """Save version control data."""
        with open(self.version_file, 'w') as f:
            json.dump(data, f, indent=2)

    def _load_version_data(self) -> Dict:
        """Load version control data."""
        with open(self.version_file, 'r') as f:
            return json.load(f)

    def _backup_database(self) -> Path:
        """Create a backup of the database."""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_path = self.db_path.parent / f"backup_{timestamp}.db"
        shutil.copy2(self.db_path, backup_path)
        return backup_path

    def apply_migrations(self, target_version: int) -> bool:
        """Apply all necessary migrations to reach target version."""
        version_data = self._load_version_data()
        current_version = version_data["current_version"]

        if current_version >= target_version:
            return True

        # Create backup before migrations
        backup_path = self._backup_database()

        try:
            with sqlite3.connect(self.db_path) as conn:
                for version in range(current_version + 1, target_version + 1):
                    migration_file = self.migrations_dir / f"v{version}.sql"
                    if not migration_file.exists():
                        raise FileNotFoundError(
                            f"Migration file for version {version} not found"
                        )

                    # Apply migration
                    with open(migration_file, 'r') as f:
                        conn.executescript(f.read())

                    # Update version data
                    version_data["migrations"].append({
                        "version": version,
                        "applied": datetime.now().isoformat(),
                        "backup": str(backup_path)
                    })

                version_data["current_version"] = target_version
                version_data["last_migration"] = datetime.now().isoformat()
                self._save_version_data(version_data)

            return True

        except Exception as e:
            # Restore from backup on failure
            if backup_path.exists():
                shutil.copy2(backup_path, self.db_path)
            raise Exception(f"Migration failed: {str(e)}")

    def create_migration(self, version: int, description: str, 
                        up_sql: str, down_sql: str = None):
        """Create a new migration file."""
        migration_file = self.migrations_dir / f"v{version}.sql"
        if migration_file.exists():
            raise FileExistsError(
                f"Migration file for version {version} already exists"
            )

        content = [
            f"-- Migration v{version}: {description}",
            f"-- Created: {datetime.now().isoformat()}",
            "",
            "-- Up",
            up_sql,
            ""
        ]

        if down_sql:
            content.extend([
                "-- Down",
                down_sql
            ])

        with open(migration_file, 'w') as f:
            f.write('\n'.join(content))

    def get_migration_history(self) -> List[Dict]:
        """Get history of applied migrations."""
        version_data = self._load_version_data()
        return version_data["migrations"]

# Example Usage:
"""
manager = MigrationManager(Path.home() / '.octavia' / 'memory.db')

# Create new migration
manager.create_migration(
    version=2,
    description="Add user_settings table",
    up_sql='''
        CREATE TABLE user_settings (
            key TEXT PRIMARY KEY,
            value TEXT NOT NULL,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP
        );
    ''',
    down_sql='''
        DROP TABLE user_settings;
    '''
)

# Apply migrations
manager.apply_migrations(target_version=2)

# Check migration history
history = manager.get_migration_history()
"""
