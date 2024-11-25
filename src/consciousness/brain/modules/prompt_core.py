"""
Core prompt management functionality for Octavia
"""

from typing import Dict, Any
from loguru import logger
import json
import time
from datetime import datetime, timedelta
from .prompt_metrics import PromptMetrics, PromptMonitor
from .prompt_capabilities import CapabilityManager

class PromptManager:
    """Core prompt management with Gemini 1.5 optimization"""
    
    # Gemini 1.5 specific configurations
    MAX_PROMPT_LENGTH = 1_000_000  # 1M tokens for Gemini 1.5
    TEMPERATURE = 0.7
    TOP_K = 20
    TOP_P = 0.95
    
    # Performance thresholds
    CPU_THRESHOLD = 80.0
    MEMORY_THRESHOLD = 85.0
    
    def __init__(self):
        """Initialize the prompt manager"""
        self.base_prompt = """You are Octavia v3, an advanced AI assistant powered by Gemini 1.5 Flash. Follow these principles:

1. Help users interact with their computer naturally and efficiently
2. Be proactive in suggesting improvements and solutions
3. Maintain strict security protocols and data protection
4. Provide clear, step-by-step explanations when needed
5. Adapt your responses based on user's technical level
6. Monitor and optimize system resource usage

Example interaction formats:
[Technical Response]
```python
# Code example with comments
def example():
    # Clear explanation
    pass
```

[UI Interaction]
1. Observe user actions
2. Provide contextual suggestions
3. Maintain non-intrusive monitoring

[System Operations]
- Validate commands before execution
- Check security implications
- Monitor resource usage"""
        
        self.capabilities = CapabilityManager()
        self.monitor = PromptMonitor()
        
        # Cache settings
        self._prompt_cache: Dict[str, Dict[str, Any]] = {}
        self.MAX_CACHE_ENTRIES = 1000
        self.CACHE_TTL = timedelta(hours=1)
    
    def _format_prompt_section(self, section_name: str, content: str) -> str:
        """Format prompt sections with clear structure"""
        return f"""[{section_name}]
{content}
---"""

    def _add_examples(self, context: Dict) -> str:
        """Add relevant examples based on context"""
        examples = []
        
        if context.get('code_related'):
            examples.append("""Example - Code Analysis:
Input: Review this function
Response: Here's the step-by-step analysis:
1. Function purpose
2. Potential issues
3. Suggested improvements""")
            
        if context.get('ui_interaction'):
            examples.append("""Example - UI Interaction:
Context: User exploring file system
Response: I notice you're browsing files. Would you like to:
1. Search for specific files
2. Get folder statistics
3. Organize files by type""")
            
        return "\n\n".join(examples) if examples else ""

    def _generate_cache_key(self, context: Dict) -> str:
        """Generate a unique cache key from context"""
        try:
            # Sort context items for consistent key generation
            sorted_items = sorted(
                (str(k), str(v)) for k, v in context.items()
                if not k.startswith('_')  # Skip internal keys
            )
            return json.dumps(sorted_items)
        except Exception as e:
            logger.error(f"Error generating cache key: {e}")
            return str(time.time())  # Fallback to timestamp

    def get_prompt(self, context: Dict) -> str:
        """Generate optimized prompt with Gemini 1.5 features"""
        start_time = time.time()
        
        try:
            # Generate cache key from context
            context_key = self._generate_cache_key(context)
            
            # Check cache first
            if context_key in self._prompt_cache:
                cached = self._prompt_cache[context_key]
                if isinstance(cached, dict) and cached.get('timestamp'):
                    if datetime.now() - cached['timestamp'] < self.CACHE_TTL:
                        return cached['prompt']
            
            # Monitor system resources
            resources = self.monitor.monitor_system_resources()
            if resources.get('cpu_usage', 0) > self.CPU_THRESHOLD or \
               resources.get('memory_usage', 0) > self.MEMORY_THRESHOLD:
                logger.warning("System resources constrained, using minimal prompt")
                return self.base_prompt
            
            # Get relevant capability modules
            active_modules = self.capabilities.get_relevant_modules(context)
            
            # Build prompt parts
            prompt_parts = [self.base_prompt]
            
            # Add active capabilities
            for module in active_modules:
                content = self.capabilities.get_capability_content(module)
                if content:
                    prompt_parts.append(self._format_prompt_section(module, content))
            
            # Add examples
            examples = self._add_examples(context)
            if examples:
                prompt_parts.append("\nExamples:\n" + examples)
            
            # Combine all parts
            final_prompt = "\n\n".join(filter(None, prompt_parts))
            
            # Apply safety filters
            final_prompt = self.capabilities.apply_safety_filters(final_prompt)
            
            # Record metrics
            generation_time = time.time() - start_time
            metrics = PromptMetrics(
                generation_time=generation_time,
                prompt_length=len(final_prompt),
                num_capabilities=len(active_modules),
                complexity_score=len(active_modules) * 0.5,
                token_count=len(final_prompt.split())
            )
            self.monitor.record_metrics(context_key, metrics)
            
            # Cache the result
            self._prompt_cache[context_key] = {
                'prompt': final_prompt,
                'timestamp': datetime.now()
            }
            
            # Optimize cache if needed
            self._optimize_cache()
            
            return final_prompt
            
        except Exception as e:
            logger.error(f"Error generating prompt: {e}")
            return self.base_prompt

    def _optimize_cache(self) -> None:
        """Optimize prompt cache size and remove expired entries"""
        try:
            current_time = datetime.now()
            
            # Remove expired entries
            expired = [
                key for key, value in self._prompt_cache.items()
                if isinstance(value, dict) and 
                current_time - value.get('timestamp', current_time) > self.CACHE_TTL
            ]
            
            for key in expired:
                del self._prompt_cache[key]
            
            # If cache is still too large, remove oldest entries
            if len(self._prompt_cache) > self.MAX_CACHE_ENTRIES:
                sorted_cache = sorted(
                    self._prompt_cache.items(),
                    key=lambda x: x[1].get('timestamp', current_time) if isinstance(x[1], dict) else current_time,
                    reverse=True
                )
                self._prompt_cache = dict(sorted_cache[:self.MAX_CACHE_ENTRIES])
            
        except Exception as e:
            logger.error(f"Error optimizing cache: {e}")

    def get_metrics_summary(self) -> Dict[str, float]:
        """Get summary of prompt generation metrics"""
        return self.monitor.get_metrics_summary()

    def get_capability_usage(self) -> Dict[str, int]:
        """Get capability usage statistics"""
        return self.capabilities.get_usage_stats()
