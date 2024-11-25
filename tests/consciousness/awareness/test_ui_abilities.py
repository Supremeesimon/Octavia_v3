"""
Tests for Octavia's UI Abilities
"""

import pytest
from unittest.mock import Mock, MagicMock, patch, AsyncMock
from consciousness.awareness.ui_abilities import UIAbilitiesRegistrar
from consciousness.awareness.abilities_awareness import AbilityAwareness, AbilityType

@pytest.fixture
def mock_ability_awareness():
    """Create mock ability awareness system"""
    awareness = AsyncMock(spec=AbilityAwareness)
    awareness.register_ability = AsyncMock()
    return awareness

@pytest.fixture
def ui_abilities(mock_ability_awareness):
    """Create UI abilities registrar"""
    registrar = UIAbilitiesRegistrar(mock_ability_awareness)
    return registrar

@pytest.mark.asyncio
async def test_ability_registration(ui_abilities, mock_ability_awareness):
    """Test registration of UI abilities"""
    # Register abilities
    await ui_abilities.register_ui_abilities()
    
    # Verify core abilities were registered
    expected_abilities = [
        "Window Management",
        "Layout Adaptation",
        "Interaction Context",
        "Mouse Tracking"
    ]
    
    # Count registered abilities
    register_calls = mock_ability_awareness.register_ability.call_args_list
    registered_names = [call.kwargs["name"] for call in register_calls]
    
    # Verify all expected abilities were registered
    for ability in expected_abilities:
        assert ability in registered_names

@pytest.mark.asyncio
async def test_window_management_registration(ui_abilities, mock_ability_awareness):
    """Test window management ability registration"""
    # Register window management
    await ui_abilities._register_window_management()
    
    # Verify registration
    mock_ability_awareness.register_ability.assert_called_with(
        name="Window Management",
        ability_type=AbilityType.UI,
        description="Manages window state and layout",
        handler=ui_abilities._handle_window_management
    )

@pytest.mark.asyncio
async def test_layout_abilities_registration(ui_abilities, mock_ability_awareness):
    """Test layout abilities registration"""
    # Register layout abilities
    await ui_abilities._register_layout_abilities()
    
    # Verify registration
    mock_ability_awareness.register_ability.assert_called_with(
        name="Layout Adaptation",
        ability_type=AbilityType.UI,
        description="Adapts UI layout based on context",
        handler=ui_abilities._handle_layout_adaptation
    )

@pytest.mark.asyncio
async def test_interaction_awareness_registration(ui_abilities, mock_ability_awareness):
    """Test interaction awareness registration"""
    # Register interaction awareness
    await ui_abilities._register_interaction_awareness()
    
    # Verify registration
    mock_ability_awareness.register_ability.assert_called_with(
        name="Interaction Context",
        ability_type=AbilityType.UI,
        description="Tracks and responds to user interactions",
        handler=ui_abilities._handle_interaction_context
    )

@pytest.mark.asyncio
async def test_mouse_tracking_registration(ui_abilities, mock_ability_awareness):
    """Test mouse tracking registration"""
    # Register mouse tracking
    await ui_abilities._register_mouse_tracking()
    
    # Verify registration
    mock_ability_awareness.register_ability.assert_called_with(
        name="Mouse Tracking",
        ability_type=AbilityType.UI,
        description="Tracks mouse position and behavior",
        handler=ui_abilities._handle_mouse_tracking
    )
