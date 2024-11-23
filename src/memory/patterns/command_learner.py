"""
Learns and suggests command patterns based on user interactions and success rates.
"""

import json
from typing import Optional, Dict, List, Tuple
from ..database.manager import DatabaseManager

class CommandPatternLearner:
    def __init__(self):
        self.db = DatabaseManager()
        self.current_pattern: Optional[int] = None  # Currently active pattern ID

    def analyze_command(self, command: str, shell_type: str) -> Dict:
        """Analyze a command to extract its pattern."""
        # Basic pattern extraction (will be enhanced)
        parts = command.split()
        base_command = parts[0] if parts else ""
        
        pattern = {
            "base_command": base_command,
            "shell_type": shell_type,
            "parameter_count": len(parts) - 1,
            "has_pipes": "|" in command,
            "has_wildcards": any(c in command for c in ["*", "?"]),
            "command_length": len(command)
        }
        return pattern

    def learn_from_success(self, command: str, shell_type: str, 
                         intent: str, success: bool,
                         context: Optional[Dict] = None):
        """Learn from command execution success or failure."""
        pattern = self.analyze_command(command, shell_type)
        pattern["intent"] = intent
        pattern["original_command"] = command
        pattern["context"] = context or {}

        # Check if similar pattern exists
        similar_patterns = self.db.get_patterns_by_type("command")
        best_match = None
        
        for p in similar_patterns:
            stored_pattern = json.loads(p["pattern_data"])
            if (stored_pattern["base_command"] == pattern["base_command"] and
                stored_pattern["intent"] == intent):
                best_match = p
                break

        if best_match:
            # Update existing pattern
            self.db.update_pattern_success_rate(best_match["id"], success)
            self.current_pattern = best_match["id"]
        else:
            # Save new pattern
            pattern_id = self.db.save_pattern(
                pattern_type="command",
                pattern_data=pattern,
                success_rate=1.0 if success else 0.0
            )
            self.current_pattern = pattern_id

    def suggest_command(self, intent: str, context: Optional[Dict] = None) -> Optional[str]:
        """Suggest a command based on intent and context."""
        patterns = self.db.get_patterns_by_type("command")
        best_match = None
        highest_score = 0.0

        for pattern in patterns:
            pattern_data = json.loads(pattern["pattern_data"])
            if pattern_data["intent"] != intent:
                continue

            # Calculate match score based on:
            # 1. Success rate
            # 2. Context similarity
            # 3. Usage count
            score = pattern["success_rate"]
            
            if context and pattern_data.get("context"):
                # Simple context matching (can be enhanced)
                matching_context = sum(
                    1 for k, v in context.items()
                    if k in pattern_data["context"] 
                    and pattern_data["context"][k] == v
                )
                score *= (1 + matching_context * 0.1)  # Boost score for matching context

            if score > highest_score:
                highest_score = score
                best_match = pattern_data

        return best_match["original_command"] if best_match else None

    def get_pattern_stats(self, intent: Optional[str] = None) -> List[Dict]:
        """Get statistics about learned patterns."""
        patterns = self.db.get_patterns_by_type("command")
        stats = []

        for pattern in patterns:
            pattern_data = json.loads(pattern["pattern_data"])
            if intent and pattern_data["intent"] != intent:
                continue
                
            stats.append({
                "intent": pattern_data["intent"],
                "command": pattern_data["original_command"],
                "success_rate": pattern["success_rate"],
                "usage_count": pattern["usage_count"]
            })

        return stats
