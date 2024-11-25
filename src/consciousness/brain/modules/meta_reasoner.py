"""
Meta-reasoning system for Octavia's predictive and fallback capabilities.
"""

from typing import Dict, List, Optional, Set
from dataclasses import dataclass
from enum import Enum
import os
from pathlib import Path
from loguru import logger

class ActionContext(Enum):
    FOLDER = "folder"
    FILE = "file"
    SYSTEM = "system"
    NETWORK = "network"
    USER = "user"

@dataclass
class ActionNode:
    """Represents a possible action and its consequences"""
    action: str
    context: ActionContext
    prerequisites: List[str]
    consequences: List[str]
    fallbacks: List['ActionStrategy']
    probability: float  # How likely this action is needed
    user_intent_signals: List[str]  # Keywords/patterns that suggest user might want this

@dataclass
class ActionStrategy:
    """A strategy for handling an action"""
    name: str
    steps: List[str]
    required_tools: List[str]
    fallback_strategy: Optional['ActionStrategy'] = None

class MetaReasoner:
    """Handles predictive reasoning and fallback strategies"""
    
    def __init__(self):
        self._action_graph = self._initialize_action_graph()
        self._context_history = []
        self._successful_strategies = {}
        
    def _initialize_action_graph(self) -> Dict[ActionContext, List[ActionNode]]:
        """Initialize the graph of possible actions and their relationships"""
        
        # Define common fallback strategies
        file_recovery_strategy = ActionStrategy(
            name="file_recovery",
            steps=[
                "check_recycle_bin",
                "check_backup_locations",
                "check_version_history",
                "scan_for_temp_files",
                "attempt_file_recovery_tools"
            ],
            required_tools=["file_recovery", "system_access"]
        )
        
        data_backup_strategy = ActionStrategy(
            name="data_backup",
            steps=[
                "create_temp_backup",
                "verify_backup_integrity",
                "store_in_safe_location"
            ],
            required_tools=["file_operations"]
        )
        
        # Define folder-related actions
        folder_actions = [
            ActionNode(
                action="navigate",
                context=ActionContext.FOLDER,
                prerequisites=["folder_exists", "have_permissions"],
                consequences=["current_dir_changed"],
                fallbacks=[
                    ActionStrategy(
                        name="folder_not_found_recovery",
                        steps=[
                            "check_parent_directory",
                            "search_similar_names",
                            "check_recent_moves",
                            "suggest_alternatives"
                        ],
                        required_tools=["file_search"],
                        fallback_strategy=file_recovery_strategy
                    )
                ],
                probability=0.9,
                user_intent_signals=["open", "go to", "show", "what's in"]
            ),
            ActionNode(
                action="organize",
                context=ActionContext.FOLDER,
                prerequisites=["folder_exists", "have_permissions"],
                consequences=["files_moved", "folders_created"],
                fallbacks=[
                    ActionStrategy(
                        name="organization_safety",
                        steps=[
                            "create_backup",
                            "test_organization_rules",
                            "apply_incrementally",
                            "verify_results"
                        ],
                        required_tools=["file_operations"],
                        fallback_strategy=data_backup_strategy
                    )
                ],
                probability=0.7,
                user_intent_signals=["organize", "clean up", "sort", "arrange"]
            )
        ]
        
        # Define file-related actions
        file_actions = [
            ActionNode(
                action="open",
                context=ActionContext.FILE,
                prerequisites=["file_exists", "have_permissions", "valid_format"],
                consequences=["file_accessed"],
                fallbacks=[
                    ActionStrategy(
                        name="file_open_recovery",
                        steps=[
                            "check_file_type",
                            "try_alternative_programs",
                            "check_file_corruption",
                            "suggest_converters"
                        ],
                        required_tools=["file_analysis"],
                        fallback_strategy=file_recovery_strategy
                    )
                ],
                probability=0.8,
                user_intent_signals=["open", "view", "show", "read"]
            )
        ]
        
        return {
            ActionContext.FOLDER: folder_actions,
            ActionContext.FILE: file_actions
        }
    
    def predict_next_actions(self, current_context: Dict) -> List[ActionNode]:
        """Predict likely next actions based on current context"""
        relevant_actions = []
        context_type = self._determine_context_type(current_context)
        
        # Get actions for this context
        possible_actions = self._action_graph.get(context_type, [])
        
        # Filter and sort by probability and relevance
        for action in possible_actions:
            # Check if prerequisites are met
            if self._check_prerequisites(action, current_context):
                # Adjust probability based on user history and current state
                adjusted_prob = self._adjust_probability(action, current_context)
                action.probability = adjusted_prob
                relevant_actions.append(action)
        
        # Sort by adjusted probability
        relevant_actions.sort(key=lambda x: x.probability, reverse=True)
        return relevant_actions
    
    def get_fallback_strategy(self, action: str, failure_type: str) -> ActionStrategy:
        """Get appropriate fallback strategy for a failed action"""
        context_type = self._determine_action_context(action)
        actions = self._action_graph.get(context_type, [])
        
        for action_node in actions:
            if action_node.action == action:
                # Find most appropriate fallback based on failure type
                for fallback in action_node.fallbacks:
                    if self._is_fallback_suitable(fallback, failure_type):
                        return fallback
        
        # Return a generic fallback if no specific one is found
        return self._get_generic_fallback()
    
    def _determine_context_type(self, context: Dict) -> ActionContext:
        """Determine the type of context we're in"""
        if context.get('current_path'):
            path = Path(context['current_path'])
            return ActionContext.FOLDER if path.is_dir() else ActionContext.FILE
        return ActionContext.SYSTEM
    
    def _check_prerequisites(self, action: ActionNode, context: Dict) -> bool:
        """Check if all prerequisites for an action are met"""
        for prereq in action.prerequisites:
            if not self._check_single_prerequisite(prereq, context):
                return False
        return True
    
    def _adjust_probability(self, action: ActionNode, context: Dict) -> float:
        """Adjust action probability based on context and history"""
        base_prob = action.probability
        
        # Adjust based on user history
        if action.action in self._successful_strategies:
            base_prob *= 1.2  # Increase probability if strategy was successful before
            
        # Adjust based on user intent signals
        if any(signal in context.get('last_message', '').lower() 
               for signal in action.user_intent_signals):
            base_prob *= 1.5  # Significant increase if user signals intent
            
        # Cap probability at 1.0
        return min(base_prob, 1.0)
    
    def _is_fallback_suitable(self, fallback: ActionStrategy, failure_type: str) -> bool:
        """Check if a fallback strategy is suitable for the type of failure"""
        # Map failure types to required tools/steps
        failure_requirements = {
            'not_found': ['file_search', 'file_recovery'],
            'permission_denied': ['permission_escalation'],
            'corruption': ['file_recovery', 'file_analysis'],
            'network_error': ['network_retry', 'local_cache']
        }
        
        required_tools = failure_requirements.get(failure_type, [])
        return all(tool in fallback.required_tools for tool in required_tools)
    
    def _get_generic_fallback(self) -> ActionStrategy:
        """Get a generic fallback strategy"""
        return ActionStrategy(
            name="generic_recovery",
            steps=[
                "analyze_error",
                "check_system_state",
                "attempt_basic_recovery",
                "notify_user"
            ],
            required_tools=["system_access"]
        )
    
    def update_success_rate(self, action: str, success: bool):
        """Update the success rate of strategies"""
        if success:
            self._successful_strategies[action] = self._successful_strategies.get(action, 0) + 1
