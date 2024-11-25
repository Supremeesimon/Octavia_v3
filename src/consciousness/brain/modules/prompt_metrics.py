"""
Metrics and monitoring for Octavia's prompt management system
"""

from dataclasses import dataclass
from datetime import datetime
import psutil
from loguru import logger
from typing import Dict, List, Optional
from collections import defaultdict

@dataclass
class PromptMetrics:
    """Metrics for prompt generation and performance"""
    generation_time: float
    prompt_length: int
    num_capabilities: int
    complexity_score: float
    token_count: int
    timestamp: datetime = datetime.now()

class PromptMonitor:
    """Handles metrics collection and system monitoring for prompt generation"""
    
    def __init__(self):
        self._metrics: Dict[str, List[PromptMetrics]] = defaultdict(list)
        self._performance_stats: Dict[str, float] = {}
        self.MAX_METRICS_HISTORY = 100
        
    def monitor_system_resources(self) -> Dict[str, float]:
        """Monitor system resource usage"""
        try:
            cpu_percent = psutil.cpu_percent(interval=0.1)
            memory = psutil.virtual_memory()
            
            stats = {
                'cpu_usage': cpu_percent,
                'memory_usage': memory.percent,
                'memory_available': memory.available / (1024 * 1024 * 1024)  # GB
            }
            
            self._performance_stats.update(stats)
            return stats
            
        except Exception as e:
            logger.error(f"Error monitoring system resources: {e}")
            return {}

    def record_metrics(self, context_key: str, metrics: PromptMetrics) -> None:
        """Record prompt generation metrics"""
        try:
            self._metrics[context_key].append(metrics)
            
            # Trim metrics history if needed
            if len(self._metrics[context_key]) > self.MAX_METRICS_HISTORY:
                self._metrics[context_key] = self._metrics[context_key][-self.MAX_METRICS_HISTORY:]
                
        except Exception as e:
            logger.error(f"Error recording metrics: {e}")

    def get_performance_stats(self) -> Dict[str, float]:
        """Get current performance statistics"""
        return self._performance_stats

    def get_metrics_summary(self, context_key: Optional[str] = None) -> Dict[str, float]:
        """Get summary of prompt metrics"""
        try:
            if context_key and context_key in self._metrics:
                metrics_list = self._metrics[context_key]
            else:
                metrics_list = [m for metrics in self._metrics.values() for m in metrics]
            
            if not metrics_list:
                return {}
            
            return {
                'avg_generation_time': sum(m.generation_time for m in metrics_list) / len(metrics_list),
                'avg_prompt_length': sum(m.prompt_length for m in metrics_list) / len(metrics_list),
                'avg_complexity': sum(m.complexity_score for m in metrics_list) / len(metrics_list),
                'total_prompts': len(metrics_list)
            }
            
        except Exception as e:
            logger.error(f"Error getting metrics summary: {e}")
            return {}
