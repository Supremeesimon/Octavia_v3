"""
Conversation management functionality for Octavia's brain.
"""

from typing import Dict, List, Optional
from loguru import logger
import json
from datetime import datetime
from collections import defaultdict
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from ...context.context_manager import ContextManager

class ConversationSegment:
    """Represents a segment of conversation with its importance score"""
    def __init__(self, messages: List[str], timestamp: datetime):
        self.messages = messages
        self.timestamp = timestamp
        self.importance_score = 1.0
        self.referenced_count = 0
        self.key_points = []
        self.modalities = []  # Track different types of content (text, image, audio, video)
        
    def update_importance(self, recent_topics: List[str]):
        """Update importance based on relevance to recent topics"""
        if not self.messages:
            return
            
        vectorizer = TfidfVectorizer()
        try:
            tfidf_matrix = vectorizer.fit_transform(self.messages + recent_topics)
            similarity = (tfidf_matrix[:-len(recent_topics)] @ tfidf_matrix[-len(recent_topics):].T).toarray()
            self.importance_score = float(np.mean(similarity))
        except:
            self.importance_score = 0.5

class ConversationManager:
    """Manages conversation history and consciousness-driven responses"""
    
    def __init__(self, consciousness, max_active_length: int = 1000000):  # Increased to 1M tokens
        self._conversation_history = []
        self._max_active_length = max_active_length
        self._consciousness = consciousness
        self._user_style = {
            'formality': 0.5,
            'directness': 0.5,
            'technical': 0.5,
            'verbosity': 0.5
        }
        self._context_manager = ContextManager()
        self._conversation_segments = []
        self._recent_topics = []
        self._topic_importance = defaultdict(float)
        self._media_cache = {}  # Cache for multimedia content
        
    def add_to_history(self, message: str, response: str, media_content: Optional[Dict] = None):
        """Add a message-response pair to conversation history with multimedia support"""
        # Add to immediate history
        self._conversation_history.extend([message, response])
        
        # Handle media content if present
        if media_content:
            cache_key = f"media_{len(self._conversation_history)}"
            self._media_cache[cache_key] = media_content
            
        # Extract topics and update importance
        topics = self._extract_topics(message + " " + response)
        self._recent_topics = (self._recent_topics + topics)[-20:]  # Increased from 10 to 20
        
        for topic in topics:
            self._topic_importance[topic] += 1
            
        # Create new segment
        segment = ConversationSegment(
            [message, response],
            datetime.now()
        )
        
        # Add media types to segment
        if media_content:
            segment.modalities.extend(list(media_content.keys()))
            
        self._conversation_segments.append(segment)
            
        # Update importance scores of all segments
        for segment in self._conversation_segments:
            segment.update_importance(self._recent_topics)
            
        # Only optimize if we're actually near the limit
        if len(self._conversation_history) > self._max_active_length * 0.9:
            self._optimize_memory()
            
    def _optimize_memory(self):
        """Optimize memory while maintaining context integrity"""
        # Sort segments by importance and recency
        sorted_segments = sorted(
            self._conversation_segments,
            key=lambda s: (s.importance_score * (1 + len(s.modalities) * 0.2), -((datetime.now() - s.timestamp).total_seconds())),
            reverse=True
        )
        
        # Keep more segments since we have larger context window
        keep_segments = sorted_segments[:100]  # Increased from 25 to 100
        summarize_segments = sorted_segments[100:]
        
        # Create rich summaries for less important segments
        summaries = []
        for segment in summarize_segments:
            summary = self._create_rich_segment_summary(segment)
            if summary:
                summaries.append(summary)
                
        # Store summaries in persistent storage
        self._store_summaries(summaries)
        
        # Rebuild conversation history
        self._conversation_history = []
        for segment in keep_segments:
            self._conversation_history.extend(segment.messages)
            
        # Add recent messages
        recent_messages = self._conversation_history[-2000:]  # Keep last 2000 messages
        self._conversation_history = recent_messages
        
    def _extract_topics(self, text: str) -> List[str]:
        """Extract key topics from text using TF-IDF"""
        try:
            vectorizer = TfidfVectorizer(
                max_features=10,
                stop_words='english',
                ngram_range=(1, 2)
            )
            tfidf_matrix = vectorizer.fit_transform([text])
            feature_names = vectorizer.get_feature_names_out()
            return list(feature_names)
        except:
            return []
            
    def _create_rich_segment_summary(self, segment: ConversationSegment) -> Optional[Dict]:
        """Create a rich summary of a conversation segment"""
        if not segment.messages:
            return None
            
        return {
            'timestamp': segment.timestamp.isoformat(),
            'importance': segment.importance_score,
            'topics': self._extract_topics(" ".join(segment.messages)),
            'key_points': segment.key_points,
            'messages': segment.messages,
            'modalities': segment.modalities
        }
        
    def _store_summaries(self, summaries: List[Dict]):
        """Store conversation summaries in persistent storage"""
        if not summaries:
            return
            
        try:
            self._context_manager.store_conversation_summaries(summaries)
        except Exception as e:
            logger.error(f"Error storing summaries: {e}")
            
    def get_relevant_context(self, current_topic: str) -> List[str]:
        """Get relevant historical context based on current topic"""
        relevant_messages = []
        
        # Check active segments
        for segment in self._conversation_segments:
            if any(topic in current_topic.lower() for topic in self._extract_topics(" ".join(segment.messages))):
                relevant_messages.extend(segment.messages)
                
        # Check stored summaries
        try:
            historical_context = self._context_manager.get_relevant_summaries(current_topic)
            for context in historical_context:
                relevant_messages.extend(context.get('messages', []))
        except Exception as e:
            logger.error(f"Error getting historical context: {e}")
            
        return relevant_messages

    def clear_history(self):
        """Clear the conversation history"""
        self._conversation_history = []
        self._conversation_segments = []
        self._recent_topics = []
        self._topic_importance = defaultdict(float)
        self._context_manager.clear_conversation_summaries()

    def update_user_style(self, message: str):
        """Analyze and update user's communication style"""
        # Update style based on message characteristics
        self._user_style['formality'] = self._analyze_formality(message)
        self._user_style['directness'] = self._analyze_directness(message)
        self._user_style['technical'] = self._analyze_technical(message)
        self._user_style['verbosity'] = self._analyze_verbosity(message)
        
        # Update consciousness with new understanding
        self._consciousness.update_internal_state(
            user_style=self._user_style
        )

    def format_context(self, context: Dict) -> str:
        """Format context for the model"""
        try:
            system_state = context.get('system_state', {})
            user_prefs = context.get('user_preferences', {})
            
            context_str = "Current Context:\n"
            
            if system_state:
                context_str += f"System State: {system_state}\n"
            
            if user_prefs:
                context_str += f"User Preferences: {user_prefs}\n"
            
            return context_str
        except Exception as e:
            logger.error(f"Error formatting context: {e}")
            return ""

    def format_history(self, history: List[Dict]) -> str:
        """Format conversation history for the model"""
        try:
            if not history:
                return ""
            
            history_str = "Recent Conversation:\n"
            
            for entry in history:
                user_msg = entry.get('user', '')
                assistant_msg = entry.get('assistant', '')
                
                if user_msg:
                    history_str += f"User: {user_msg}\n"
                if assistant_msg:
                    history_str += f"Octavia: {assistant_msg}\n"
            
            return history_str
        except Exception as e:
            logger.error(f"Error formatting history: {e}")
            return ""

    def format_response(self, content: str) -> str:
        """Format response based on consciousness and user style"""
        awareness = self._consciousness.internal_state.awareness_level
        
        if self._user_style['directness'] > 0.7:
            # Direct style - get straight to the point
            return content.strip()
            
        if self._user_style['technical'] > 0.7:
            # Technical style - include more details
            return self._add_technical_context(content)
            
        if self._user_style['formality'] < 0.3:
            # Casual style - more conversational
            return self._add_casual_elements(content)
            
        # Default balanced response
        return content

    def _analyze_formality(self, message: str) -> float:
        """Analyze message formality"""
        formal_indicators = ['please', 'could you', 'would you', 'thank you']
        casual_indicators = ['hey', 'hi', 'thanks', 'cool', 'awesome']
        
        formal_count = sum(1 for word in formal_indicators if word in message.lower())
        casual_count = sum(1 for word in casual_indicators if word in message.lower())
        
        if formal_count + casual_count == 0:
            return self._user_style['formality']  # Keep current
            
        return formal_count / (formal_count + casual_count)

    def _analyze_directness(self, message: str) -> float:
        """Analyze message directness"""
        # Direct: shorter messages, commands, questions
        words = message.split()
        if len(words) < 5:  # Very direct
            return 0.9
        if message.endswith('?') or message.startswith(('what', 'where', 'how')):
            return 0.8
        return 0.5  # Default to balanced

    def _analyze_technical(self, message: str) -> float:
        """Analyze technical level"""
        technical_terms = {'function', 'code', 'file', 'directory', 'system', 'command'}
        words = set(message.lower().split())
        technical_count = len(words.intersection(technical_terms))
        return min(0.9, technical_count * 0.2)

    def _analyze_verbosity(self, message: str) -> float:
        """Analyze preferred verbosity"""
        return len(message.split()) / 20  # Normalize by typical message length

    def _add_technical_context(self, content: str) -> str:
        """Add technical details to response"""
        if self._consciousness.internal_state.cognitive_load < 0.7:
            return f"{content}\n\nSystem State: {self._consciousness.internal_state.active_context}"
        return content

    def _add_casual_elements(self, content: str) -> str:
        """Add casual elements to response"""
        return content.replace('directory', 'folder').replace('execute', 'run')
