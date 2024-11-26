"""
Octavia's Configuration System
"""

import os
from pathlib import Path
from typing import Dict, Any

class Config:
    """Configuration management for Octavia"""
    
    def __init__(self):
        # Base paths
        self.BASE_DIR = Path(os.path.dirname(os.path.abspath(__file__)))
        self.DATA_DIR = self.BASE_DIR / "data"
        self.DB_DIR = self.DATA_DIR / "db"
        
        # Create necessary directories
        self.DATA_DIR.mkdir(exist_ok=True)
        self.DB_DIR.mkdir(exist_ok=True)
        
        # Database paths
        self.ABILITIES_DB = self.DB_DIR / "abilities.db"
        self.TASKS_DB = self.DB_DIR / "tasks.db"
        self.MEMORY_DB = self.DB_DIR / "memory.db"
        
        # API Configuration
        self.GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")
        
        # Model Configuration
        self.DEFAULT_MODEL = "gemini-1.5-flash"  # Updated to latest model
        
        # System Configuration
        self.DEFAULT_TEMPERATURE = 0.7
        self.MAX_OUTPUT_TOKENS = 2048
        self.TOP_K = 20
        self.TOP_P = 0.95
        self.CANDIDATE_COUNT = 1
        self.MAX_ACTIVE_LENGTH = 1000000  # 1M tokens for conversation history
        
    @property
    def as_dict(self) -> Dict[str, Any]:
        """Return configuration as a dictionary"""
        return {
            "base_dir": str(self.BASE_DIR),
            "data_dir": str(self.DATA_DIR),
            "db_dir": str(self.DB_DIR),
            "abilities_db": str(self.ABILITIES_DB),
            "tasks_db": str(self.TASKS_DB),
            "memory_db": str(self.MEMORY_DB),
            "default_model": self.DEFAULT_MODEL,
            "temperature": self.DEFAULT_TEMPERATURE,
            "max_output_tokens": self.MAX_OUTPUT_TOKENS,
            "top_k": self.TOP_K,
            "top_p": self.TOP_P,
            "candidate_count": self.CANDIDATE_COUNT,
            "max_active_length": self.MAX_ACTIVE_LENGTH
        }
