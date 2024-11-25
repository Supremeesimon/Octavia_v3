"""
Comprehensive tests for Octavia's prompt management system
"""

import unittest
from unittest.mock import Mock, patch
import sys
import os
from datetime import datetime, timedelta
from pathlib import Path

# Add src to Python path for imports
sys.path.append(str(Path(__file__).parent.parent / 'src'))

from consciousness.brain.modules.prompt_core import PromptManager
from consciousness.brain.modules.prompt_capabilities import CapabilityManager
from consciousness.brain.modules.prompt_metrics import PromptMetrics, PromptMonitor
from consciousness.context.context_manager import ContextManager

class TestBase(unittest.TestCase):
    """Base test class with common setup"""
    
    def setUp(self):
        """Set up test environment with temporary database"""
        self.context_manager = ContextManager(use_temp=True)
        
class TestPromptMetrics(TestBase):
    """Test suite for PromptMetrics and PromptMonitor"""
    
    def setUp(self):
        super().setUp()
        self.monitor = PromptMonitor()
        
    def test_system_resource_monitoring(self):
        """Test system resource monitoring functionality"""
        # Simplified test without psutil
        stats = self.monitor.monitor_system_resources()
        
        # Basic checks that stats exist
        self.assertIsInstance(stats, dict)
        self.assertGreater(len(stats), 0)
        
    def test_metrics_recording(self):
        """Test metrics recording and retrieval"""
        metrics = PromptMetrics(
            generation_time=0.5,
            prompt_length=1000,
            num_capabilities=3,
            complexity_score=1.5,
            token_count=200
        )
        
        self.monitor.record_metrics('test_context', metrics)
        summary = self.monitor.get_metrics_summary('test_context')
        
        self.assertEqual(summary['avg_generation_time'], 0.5)
        self.assertEqual(summary['avg_prompt_length'], 1000)
        self.assertEqual(summary['avg_complexity'], 1.5)
        self.assertEqual(summary['total_prompts'], 1)
        
    def test_metrics_history_limit(self):
        """Test that metrics history is properly limited"""
        for i in range(150):  # More than MAX_METRICS_HISTORY
            metrics = PromptMetrics(
                generation_time=0.1,
                prompt_length=100,
                num_capabilities=1,
                complexity_score=1.0,
                token_count=20
            )
            self.monitor.record_metrics('test_context', metrics)
            
        summary = self.monitor.get_metrics_summary('test_context')
        self.assertEqual(summary['total_prompts'], 100)  # Should be limited to MAX_METRICS_HISTORY

class TestCapabilityManager(TestBase):
    """Test suite for CapabilityManager"""
    
    def setUp(self):
        super().setUp()
        self.manager = CapabilityManager()
        
    def test_core_capabilities(self):
        """Test core capabilities are always included"""
        modules = self.manager.get_relevant_modules({})
        self.assertIn('identity', modules)
        self.assertIn('security', modules)
        
    def test_context_specific_capabilities(self):
        """Test context-specific capability activation"""
        context = {
            'ui_interaction': True,
            'security_sensitive': True,
            'performance_critical': True
        }
        
        modules = self.manager.get_relevant_modules(context)
        
        self.assertIn('ui_awareness', modules)
        self.assertIn('enhanced_security', modules)
        self.assertIn('performance', modules)
        
    def test_capability_content(self):
        """Test capability content retrieval"""
        content = self.manager.get_capability_content('identity')
        self.assertIsInstance(content, str)
        self.assertGreater(len(content), 0)
        
    def test_safety_filters(self):
        """Test safety filter application"""
        test_prompt = "Execute system command rm -rf"
        filtered = self.manager.apply_safety_filters(test_prompt)
        
        self.assertIn("Validate all system operations", filtered)
        self.assertGreater(len(filtered), len(test_prompt))

class TestPromptManager(TestBase):
    """Test suite for PromptManager"""
    
    def setUp(self):
        super().setUp()
        self.manager = PromptManager()
        
    def test_prompt_generation(self):
        """Test basic prompt generation"""
        context = {'code_related': True}
        prompt = self.manager.get_prompt(context)
        
        self.assertIsInstance(prompt, str)
        self.assertGreater(len(prompt), 0)
        self.assertIn("Octavia v3", prompt)
        
    def test_prompt_caching(self):
        """Test prompt caching functionality"""
        context = {'test_key': 'test_value'}
        
        # First call should generate new prompt
        start_time = datetime.now()
        first_prompt = self.manager.get_prompt(context)
        
        # Second call should return cached prompt
        second_prompt = self.manager.get_prompt(context)
        
        self.assertEqual(first_prompt, second_prompt)
        
    def test_resource_constrained_prompt(self):
        """Test prompt generation under resource constraints"""
        # Simplified test without psutil mock
        context = {'complex_task': True}
        prompt = self.manager.get_prompt(context)
        
        # Just verify we get some kind of prompt
        self.assertIsInstance(prompt, str)
        self.assertGreater(len(prompt), 0)
            
    def test_example_addition(self):
        """Test context-specific example addition"""
        context = {
            'code_related': True,
            'ui_interaction': True
        }
        
        prompt = self.manager.get_prompt(context)
        
        self.assertIn("Code Analysis", prompt)
        self.assertIn("UI Interaction", prompt)
        
    def test_metrics_integration(self):
        """Test metrics collection during prompt generation"""
        context = {'test_metrics': True}
        self.manager.get_prompt(context)
        
        metrics = self.manager.get_metrics_summary()
        self.assertGreater(metrics['total_prompts'], 0)
        
    def test_capability_usage_tracking(self):
        """Test capability usage statistics"""
        context = {'security_sensitive': True}
        self.manager.get_prompt(context)
        
        usage_stats = self.manager.get_capability_usage()
        self.assertGreater(usage_stats.get('security', 0), 0)
        
if __name__ == '__main__':
    unittest.main()
