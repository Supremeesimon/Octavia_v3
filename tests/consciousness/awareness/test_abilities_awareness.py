"""
Tests for the Abilities Awareness System
"""

import pytest
import asyncio
from pathlib import Path
import tempfile
import json
from datetime import datetime, timedelta

from src.consciousness.awareness.abilities_awareness import (
    AbilityAwareness,
    AbilityType,
    AbilityStatus,
    AbilityMetrics
)

@pytest.fixture
def abilities_db():
    """Create a temporary database for testing"""
    with tempfile.NamedTemporaryFile() as tmp:
        yield tmp.name

@pytest.fixture
def ability_awareness(abilities_db):
    """Create an AbilityAwareness instance with temporary database"""
    return AbilityAwareness(abilities_db)

@pytest.mark.asyncio
async def test_register_ability(ability_awareness):
    """Test registering a new ability"""
    name = "Code Analysis"
    description = "Analyze code structure and patterns"
    ability_type = AbilityType.COGNITION
    requirements = {
        "tools": ["ast", "regex"],
        "memory": "medium"
    }
    metadata = {
        "contexts": [
            {"domain": "code", "language": "python"},
            {"domain": "analysis", "type": "static"}
        ]
    }
    
    ability_id = await ability_awareness.register_ability(
        name=name,
        description=description,
        ability_type=ability_type,
        requirements=requirements,
        metadata=metadata
    )
    
    assert ability_id.startswith("ability_")
    assert ability_id in ability_awareness._active_abilities
    assert ability_awareness._active_abilities[ability_id]["name"] == name
    assert ability_awareness._active_abilities[ability_id]["type"] == ability_type
    assert ability_awareness._active_abilities[ability_id]["status"] == AbilityStatus.ACTIVE

@pytest.mark.asyncio
async def test_ability_metrics(ability_awareness):
    """Test ability metrics tracking"""
    # Register ability
    ability_id = await ability_awareness.register_ability(
        name="Test Ability",
        description="Testing metrics",
        ability_type=AbilityType.COGNITION
    )
    
    # Record successful use
    await ability_awareness.record_ability_use(
        ability_id=ability_id,
        success=True,
        response_time=0.5,
        context={"test": True}
    )
    
    # Get metrics
    metrics = await ability_awareness.get_ability_metrics(ability_id)
    
    assert metrics is not None
    assert metrics.usage_count == 1
    assert metrics.success_rate == 1.0
    assert metrics.avg_response_time == 0.5
    assert metrics.last_used is not None
    assert 0 <= metrics.confidence_level <= 1

@pytest.mark.asyncio
async def test_ability_status_updates(ability_awareness):
    """Test updating ability status"""
    ability_id = await ability_awareness.register_ability(
        name="Status Test",
        description="Testing status updates",
        ability_type=AbilityType.ACTION
    )
    
    # Update to inactive
    await ability_awareness.update_ability_status(
        ability_id,
        AbilityStatus.INACTIVE,
        reason="maintenance"
    )
    
    assert ability_awareness._active_abilities[ability_id]["status"] == AbilityStatus.INACTIVE

@pytest.mark.asyncio
async def test_find_relevant_abilities(ability_awareness):
    """Test finding relevant abilities"""
    # Register abilities with different contexts
    context1 = {
        "contexts": [
            {"domain": "code", "language": "python"},
            {"domain": "testing", "type": "unit"}
        ]
    }
    
    context2 = {
        "contexts": [
            {"domain": "code", "language": "javascript"},
            {"domain": "testing", "type": "integration"}
        ]
    }
    
    ability1_id = await ability_awareness.register_ability(
        name="Python Testing",
        description="Python test capabilities",
        ability_type=AbilityType.COGNITION,
        metadata=context1
    )
    
    ability2_id = await ability_awareness.register_ability(
        name="JS Testing",
        description="JavaScript test capabilities",
        ability_type=AbilityType.COGNITION,
        metadata=context2
    )
    
    # Record successful uses to build confidence
    for _ in range(5):
        await ability_awareness.record_ability_use(
            ability1_id,
            success=True,
            response_time=0.5
        )
        await ability_awareness.record_ability_use(
            ability2_id,
            success=True,
            response_time=0.5
        )
    
    # Search context
    search_context = {
        "domain": "code",
        "language": "python"
    }
    
    relevant = await ability_awareness.find_relevant_abilities(search_context)
    
    assert len(relevant) > 0
    assert all(ability["confidence"] > 0.5 for ability in relevant)
    # Python testing should be more relevant than JS testing
    python_relevance = next(a["relevance"] for a in relevant if a["id"] == ability1_id)
    js_relevance = next(a["relevance"] for a in relevant if a["id"] == ability2_id)
    assert python_relevance > js_relevance

@pytest.mark.asyncio
async def test_ability_suggestions(ability_awareness):
    """Test getting ability suggestions"""
    # Register some abilities and build usage history
    ability_ids = []
    for i in range(3):
        ability_id = await ability_awareness.register_ability(
            name=f"Test Ability {i}",
            description=f"Test ability {i}",
            ability_type=AbilityType.COGNITION
        )
        ability_ids.append(ability_id)
        
        # Record varying levels of success
        success_rate = (i + 1) / 3  # 0.33, 0.67, 1.0
        for _ in range(10):
            await ability_awareness.record_ability_use(
                ability_id,
                success=_ < (10 * success_rate),  # Vary success rate
                response_time=0.5
            )
    
    # Get suggestions excluding first ability
    current_abilities = {ability_ids[0]}
    context = {"test": True}
    
    suggestions = await ability_awareness.get_ability_suggestions(
        context,
        current_abilities
    )
    
    assert len(suggestions) > 0
    assert ability_ids[0] not in [s["id"] for s in suggestions]
    # Higher success rate abilities should be suggested first
    assert suggestions[0]["id"] == ability_ids[2]  # Highest success rate

def test_ability_relevance_calculation(ability_awareness):
    """Test ability relevance calculation"""
    current_context = {
        "domain": "testing",
        "tags": ["python", "unit"],
        "complexity": "medium"
    }
    
    ability_contexts = [
        {
            "domain": "testing",
            "tags": ["python", "integration"],
            "complexity": "medium"
        },
        {
            "domain": "development",
            "tags": ["java"],
            "complexity": "high"
        }
    ]
    
    relevance = ability_awareness._calculate_ability_relevance(
        current_context,
        ability_contexts
    )
    
    assert 0 <= relevance <= 1
    assert relevance > 0.5  # Should be relatively high for first context

@pytest.mark.asyncio
async def test_error_handling(ability_awareness):
    """Test error handling in ability operations"""
    # Test invalid ability ID
    await ability_awareness.update_ability_status(
        "invalid_id",
        AbilityStatus.INACTIVE
    )
    
    # Test invalid metrics recording
    await ability_awareness.record_ability_use(
        "invalid_id",
        success=True,
        response_time=-1  # Invalid response time
    )
    
    # Test invalid ability registration
    invalid_id = await ability_awareness.register_ability(
        name="",  # Invalid empty name
        description="Test",
        ability_type=AbilityType.COGNITION
    )
    assert invalid_id == ""

if __name__ == "__main__":
    pytest.main([__file__])
