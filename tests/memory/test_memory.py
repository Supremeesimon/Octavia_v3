"""
Tests for Octavia's memory system.
"""

import unittest
import tempfile
import json
from pathlib import Path
from datetime import datetime
from src.memory.database.manager import DatabaseManager
from src.memory.patterns.command_learner import CommandPatternLearner
from src.memory.context.conversation import ConversationManager
from src.memory.integration import MemoryIntegration

class TestDatabaseManager(unittest.TestCase):
    def setUp(self):
        # Create temporary database for testing
        self.temp_dir = tempfile.mkdtemp()
        self.db_path = Path(self.temp_dir) / "test_memory.db"
        self.db = DatabaseManager()

    def test_conversation_crud(self):
        """Test conversation CRUD operations."""
        # Create
        test_message = "test"
        test_response = "response"
        
        conv_id = self.db.save_conversation(
            user_message=test_message,
            octavia_response=test_response,
            context_data={"test": "data"},
            conversation_id="test_conv"
        )
        self.assertIsNotNone(conv_id)

        # Read
        conversations = self.db.get_recent_conversations(limit=1)
        self.assertEqual(len(conversations), 1)
        self.assertEqual(conversations[0]["user_message"], test_message)

    def test_command_history(self):
        """Test command history operations."""
        # Save command
        cmd_id = self.db.save_command(
            command="dir",
            shell_type="cmd",
            success=True
        )
        self.assertIsNotNone(cmd_id)

        # Get history
        history = self.db.get_command_history(limit=1)
        self.assertEqual(len(history), 1)
        self.assertEqual(history[0]["command"], "dir")

    def test_preferences(self):
        """Test preference operations."""
        # Set preference
        self.db.set_preference("test_key", "test_value")

        # Get preference
        value = self.db.get_preference("test_key")
        self.assertEqual(value, "test_value")

class TestCommandLearner(unittest.TestCase):
    def setUp(self):
        self.learner = CommandPatternLearner()

    def test_command_learning(self):
        """Test command pattern learning."""
        # Learn command
        self.learner.learn_from_success(
            command="Get-ChildItem Downloads",
            shell_type="powershell",
            intent="list_files",
            success=True
        )

        # Get suggestion
        suggestion = self.learner.suggest_command("list_files")
        self.assertEqual(suggestion, "Get-ChildItem Downloads")

    def test_pattern_analysis(self):
        """Test command pattern analysis."""
        pattern = self.learner.analyze_command(
            "Get-ChildItem Downloads | Sort-Object",
            "powershell"
        )
        self.assertEqual(pattern["base_command"], "Get-ChildItem")
        self.assertTrue(pattern["has_pipes"])

class TestConversationManager(unittest.TestCase):
    def setUp(self):
        self.conversation = ConversationManager()

    def test_conversation_context(self):
        """Test conversation context management."""
        # Add exchange
        self.conversation.add_exchange(
            user_message="test",
            octavia_response="response",
            additional_context={"test": "data"}
        )

        # Get context
        context = self.conversation.get_conversation_context()
        self.assertEqual(context["test"], "data")

    def test_new_conversation(self):
        """Test new conversation creation."""
        old_id = self.conversation.current_conversation_id
        self.conversation.start_new_conversation()
        new_id = self.conversation.current_conversation_id
        self.assertNotEqual(old_id, new_id)

class TestMemoryIntegration(unittest.TestCase):
    def setUp(self):
        self.memory = MemoryIntegration()

    def test_full_interaction(self):
        """Test complete interaction flow."""
        # Before response
        context = self.memory.before_response("test message")
        self.assertIn("recent_conversations", context)

        # After response
        self.memory.after_response(
            user_message="test message",
            octavia_response="test response",
            executed_command="dir",
            command_success=True,
            command_intent="list_files"
        )

        # Get suggestion
        suggestion = self.memory.suggest_command("list_files")
        self.assertIsNotNone(suggestion)

if __name__ == '__main__':
    unittest.main()
