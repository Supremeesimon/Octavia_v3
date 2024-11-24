"""
Tests for the Task Awareness System
"""

import pytest
import asyncio
from pathlib import Path
import tempfile
import json
from datetime import datetime

from src.consciousness.awareness.task_awareness import (
    TaskAwareness,
    TaskStatus,
    TaskPriority
)

@pytest.fixture
def task_db():
    """Create a temporary database for testing"""
    with tempfile.NamedTemporaryFile() as tmp:
        yield tmp.name

@pytest.fixture
def task_awareness(task_db):
    """Create a TaskAwareness instance with temporary database"""
    return TaskAwareness(task_db)

@pytest.mark.asyncio
async def test_create_task(task_awareness):
    """Test creating a new task"""
    title = "Test Task"
    description = "This is a test task"
    context = {
        "domain": "testing",
        "tags": ["test", "unit"]
    }
    
    task_id = await task_awareness.create_task(
        title=title,
        description=description,
        priority=TaskPriority.HIGH,
        context=context
    )
    
    assert task_id.startswith("task_")
    assert task_id in task_awareness._active_tasks
    assert task_awareness._active_tasks[task_id]["title"] == title
    assert task_awareness._active_tasks[task_id]["status"] == TaskStatus.PENDING
    assert task_awareness._active_tasks[task_id]["priority"] == TaskPriority.HIGH

@pytest.mark.asyncio
async def test_task_dependencies(task_awareness):
    """Test task dependency chain"""
    # Create parent task
    parent_id = await task_awareness.create_task(
        title="Parent Task",
        description="Parent task description"
    )
    
    # Create child task depending on parent
    child_id = await task_awareness.create_task(
        title="Child Task",
        description="Child task description",
        depends_on=[parent_id]
    )
    
    # Get task chain
    chain = await task_awareness.get_task_chain(child_id)
    
    assert len(chain) == 2
    assert chain[0]["id"] == child_id
    assert chain[1]["id"] == parent_id

@pytest.mark.asyncio
async def test_update_task_status(task_awareness):
    """Test updating task status"""
    task_id = await task_awareness.create_task(
        title="Status Test",
        description="Testing status updates"
    )
    
    metadata = {"reason": "completed successfully"}
    await task_awareness.update_task_status(
        task_id,
        TaskStatus.COMPLETED,
        metadata
    )
    
    assert task_awareness._active_tasks[task_id]["status"] == TaskStatus.COMPLETED

@pytest.mark.asyncio
async def test_related_tasks(task_awareness):
    """Test finding related tasks"""
    # Create tasks with similar context
    context1 = {
        "domain": "testing",
        "tags": ["unit", "async"],
        "priority": "high"
    }
    
    context2 = {
        "domain": "testing",
        "tags": ["unit", "sync"],
        "priority": "medium"
    }
    
    task1_id = await task_awareness.create_task(
        title="Task 1",
        description="First task",
        context=context1
    )
    
    task2_id = await task_awareness.create_task(
        title="Task 2",
        description="Second task",
        context=context2
    )
    
    # Search for related tasks
    search_context = {
        "domain": "testing",
        "tags": ["unit"]
    }
    
    related = await task_awareness.get_related_tasks(search_context)
    
    assert len(related) > 0
    assert all(task["relevance"] > 0.5 for task in related)

@pytest.mark.asyncio
async def test_context_relevance(task_awareness):
    """Test context relevance calculation"""
    context1 = {
        "tags": ["python", "testing"],
        "priority": "high"
    }
    
    context2 = {
        "tags": ["python", "development"],
        "priority": "high"
    }
    
    relevance = task_awareness._calculate_context_relevance(context1, context2)
    assert 0 <= relevance <= 1
    
    # Test exact match
    assert task_awareness._calculate_context_relevance("test", "test") == 1.0
    
    # Test complete mismatch
    assert task_awareness._calculate_context_relevance("test", "other") == 0.0
    
    # Test list similarity
    list1 = ["a", "b", "c"]
    list2 = ["b", "c", "d"]
    relevance = task_awareness._calculate_context_relevance(list1, list2)
    assert relevance == 0.5  # 2 common elements out of 4 total unique elements

def test_parse_context(task_awareness):
    """Test context string parsing"""
    context_str = "type1:{\"key\":\"value\"},type2:[1,2,3]"
    parsed = task_awareness._parse_context(context_str)
    
    assert isinstance(parsed, dict)
    assert "type1" in parsed
    assert parsed["type1"] == {"key": "value"}
    assert "type2" in parsed
    assert parsed["type2"] == [1, 2, 3]

@pytest.mark.asyncio
async def test_error_handling(task_awareness):
    """Test error handling in task operations"""
    # Test invalid task ID
    await task_awareness.update_task_status(
        "invalid_id",
        TaskStatus.COMPLETED
    )
    
    # Test invalid context format
    invalid_context = {"invalid": object()}
    task_id = await task_awareness.create_task(
        title="Invalid Context",
        description="Testing invalid context",
        context=invalid_context
    )
    assert task_id == ""  # Should fail gracefully

if __name__ == "__main__":
    pytest.main([__file__])
