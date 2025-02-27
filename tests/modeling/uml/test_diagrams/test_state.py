"""Tests for the State Diagram Generator"""

import pytest
from pathlib import Path
from uuid import uuid4

from src.modeling.uml.core import Model, Class, Operation
from src.modeling.uml.diagrams.state import (
    StateDiagramGenerator,
    State,
    Transition,
    StateType,
    Action
)

@pytest.fixture
def model():
    """Create a test model"""
    return Model(name="TestModel")

@pytest.fixture
def generator(model):
    """Create a test diagram generator"""
    return StateDiagramGenerator(model)

def test_basic_state_machine(generator):
    """Test basic state machine creation"""
    # Create states
    initial = State(
        id=str(uuid4()),
        name="Initial",
        state_type=StateType.INITIAL
    )
    idle = State(
        id=str(uuid4()),
        name="Idle",
        state_type=StateType.NORMAL
    )
    processing = State(
        id=str(uuid4()),
        name="Processing",
        state_type=StateType.NORMAL,
        entry_actions=[Action("startProcess()")],
        exit_actions=[Action("cleanup()")]
    )
    final = State(
        id=str(uuid4()),
        name="Final",
        state_type=StateType.FINAL
    )
    
    # Add states
    for state in [initial, idle, processing, final]:
        generator.add_state(state)
    
    # Add transitions
    generator.add_transition(Transition(
        source=initial.id,
        target=idle.id
    ))
    generator.add_transition(Transition(
        source=idle.id,
        target=processing.id,
        trigger="start",
        guard="[isValid]"
    ))
    generator.add_transition(Transition(
        source=processing.id,
        target=final.id,
        trigger="complete"
    ))
    
    # Generate diagram
    diagram = generator.generate()
    assert diagram is not None
    assert len(generator.states) == 4
    assert len(generator.transitions) == 3

def test_composite_states(generator):
    """Test composite state handling"""
    # Create composite state
    operating = State(
        id=str(uuid4()),
        name="Operating",
        state_type=StateType.NORMAL
    )
    
    # Create substates
    initializing = State(
        id=str(uuid4()),
        name="Initializing",
        state_type=StateType.NORMAL,
        parent=operating.id
    )
    running = State(
        id=str(uuid4()),
        name="Running",
        state_type=StateType.NORMAL,
        parent=operating.id
    )
    paused = State(
        id=str(uuid4()),
        name="Paused",
        state_type=StateType.NORMAL,
        parent=operating.id
    )
    
    # Add states
    generator.add_state(operating)
    for state in [initializing, running, paused]:
        generator.add_state(state)
    
    # Add transitions
    generator.add_transition(Transition(
        source=initializing.id,
        target=running.id,
        trigger="initialized"
    ))
    generator.add_transition(Transition(
        source=running.id,
        target=paused.id,
        trigger="pause"
    ))
    generator.add_transition(Transition(
        source=paused.id,
        target=running.id,
        trigger="resume"
    ))
    
    # Generate diagram
    diagram = generator.generate()
    assert diagram is not None
    assert len(generator.states) == 4
    assert len(generator.transitions) == 3
    assert len([s for s in generator.states.values() if s.parent == operating.id]) == 3

def test_orthogonal_regions(generator):
    """Test orthogonal regions in composite states"""
    # Create main composite state
    system = State(
        id=str(uuid4()),
        name="System",
        state_type=StateType.NORMAL
    )
    
    # Create states for first region (Power)
    power_states = {
        "off": State(id=str(uuid4()), name="Off", state_type=StateType.NORMAL, region="Power"),
        "on": State(id=str(uuid4()), name="On", state_type=StateType.NORMAL, region="Power")
    }
    
    # Create states for second region (Operation)
    operation_states = {
        "idle": State(id=str(uuid4()), name="Idle", state_type=StateType.NORMAL, region="Operation"),
        "active": State(id=str(uuid4()), name="Active", state_type=StateType.NORMAL, region="Operation")
    }
    
    # Add all states
    generator.add_state(system)
    for state in [*power_states.values(), *operation_states.values()]:
        state.parent = system.id
        generator.add_state(state)
    
    # Add transitions for power region
    generator.add_transition(Transition(
        source=power_states["off"].id,
        target=power_states["on"].id,
        trigger="powerOn"
    ))
    generator.add_transition(Transition(
        source=power_states["on"].id,
        target=power_states["off"].id,
        trigger="powerOff"
    ))
    
    # Add transitions for operation region
    generator.add_transition(Transition(
        source=operation_states["idle"].id,
        target=operation_states["active"].id,
        trigger="start"
    ))
    generator.add_transition(Transition(
        source=operation_states["active"].id,
        target=operation_states["idle"].id,
        trigger="stop"
    ))
    
    # Generate diagram
    diagram = generator.generate()
    assert diagram is not None
    assert len(generator.states) == 5  # system + 2 power states + 2 operation states
    assert len(generator.transitions) == 4

def test_history_states(generator):
    """Test history state handling"""
    # Create composite state
    composite = State(
        id=str(uuid4()),
        name="Composite",
        state_type=StateType.NORMAL
    )
    
    # Create history state
    history = State(
        id=str(uuid4()),
        name="H",
        state_type=StateType.HISTORY,
        parent=composite.id
    )
    
    # Create normal states
    state1 = State(
        id=str(uuid4()),
        name="State1",
        state_type=StateType.NORMAL,
        parent=composite.id
    )
    state2 = State(
        id=str(uuid4()),
        name="State2",
        state_type=StateType.NORMAL,
        parent=composite.id
    )
    
    # Add states
    for state in [composite, history, state1, state2]:
        generator.add_state(state)
    
    # Add transitions
    generator.add_transition(Transition(
        source=history.id,
        target=state1.id
    ))
    generator.add_transition(Transition(
        source=state1.id,
        target=state2.id,
        trigger="next"
    ))
    
    # Generate diagram
    diagram = generator.generate()
    assert diagram is not None
    assert len(generator.states) == 4
    assert len(generator.transitions) == 2

def test_from_class(generator):
    """Test creating state diagram from class"""
    # Create class with state-related operations
    cls = Class(
        name="Document",
        operations=[
            Operation(name="create"),
            Operation(name="submit"),
            Operation(name="approve"),
            Operation(name="reject")
        ]
    )
    
    # Generate state diagram from class
    generator.from_class(cls)
    
    # Verify states and transitions were created
    assert len(generator.states) >= 1
    assert len(generator.transitions) >= 1

def test_state_validation(generator):
    """Test state validation"""
    # Test duplicate state ID
    state_id = str(uuid4())
    state1 = State(
        id=state_id,
        name="State1",
        state_type=StateType.NORMAL
    )
    state2 = State(
        id=state_id,
        name="State2",
        state_type=StateType.NORMAL
    )
    
    generator.add_state(state1)
    with pytest.raises(ValueError):
        generator.add_state(state2)
    
    # Test invalid parent reference
    with pytest.raises(ValueError):
        generator.add_state(State(
            id=str(uuid4()),
            name="Invalid",
            state_type=StateType.NORMAL,
            parent=str(uuid4())
        ))

def test_transition_validation(generator):
    """Test transition validation"""
    state = State(
        id=str(uuid4()),
        name="TestState",
        state_type=StateType.NORMAL
    )
    generator.add_state(state)
    
    # Test invalid source
    with pytest.raises(ValueError):
        generator.add_transition(Transition(
            source=str(uuid4()),
            target=state.id
        ))
    
    # Test invalid target
    with pytest.raises(ValueError):
        generator.add_transition(Transition(
            source=state.id,
            target=str(uuid4())
        ))

def test_action_validation(generator):
    """Test action validation"""
    # Test empty action
    with pytest.raises(ValueError):
        State(
            id=str(uuid4()),
            name="TestState",
            state_type=StateType.NORMAL,
            entry_actions=[Action("")]
        )
    
    # Test invalid action format
    with pytest.raises(ValueError):
        State(
            id=str(uuid4()),
            name="TestState",
            state_type=StateType.NORMAL,
            do_actions=[Action("invalid action format")]
        )
