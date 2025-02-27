"""Tests for the Sequence Diagram Generator"""

import pytest
from pathlib import Path
from uuid import uuid4

from src.modeling.uml.core import Model, Operation, Parameter
from src.modeling.uml.diagrams.sequence import (
    SequenceDiagramGenerator,
    Lifeline,
    SequenceMessage,
    MessageType,
    ActivationBox
)

@pytest.fixture
def model():
    """Create a test model"""
    return Model(name="TestModel")

@pytest.fixture
def generator(model):
    """Create a test diagram generator"""
    return SequenceDiagramGenerator(model)

def test_basic_sequence(generator):
    """Test basic sequence diagram creation"""
    # Add lifelines
    generator.add_lifeline("user", "User", is_actor=True)
    generator.add_lifeline("controller", "OrderController")
    generator.add_lifeline("service", "OrderService")
    
    # Add messages
    generator.add_message(
        source="user",
        target="controller",
        message="placeOrder()",
        message_type=MessageType.SYNCHRONOUS
    )
    generator.add_message(
        source="controller",
        target="service",
        message="createOrder()",
        message_type=MessageType.SYNCHRONOUS,
        return_value="orderId"
    )
    generator.add_message(
        source="service",
        target="controller",
        message="return orderId",
        message_type=MessageType.RETURN
    )
    generator.add_message(
        source="controller",
        target="user",
        message="return confirmation",
        message_type=MessageType.RETURN
    )
    
    # Generate diagram
    diagram = generator.generate()
    assert diagram is not None
    assert len(generator.lifelines) == 3
    assert len(generator.messages) == 4

def test_async_messages(generator):
    """Test asynchronous message handling"""
    # Add lifelines
    generator.add_lifeline("client", "Client")
    generator.add_lifeline("queue", "MessageQueue")
    generator.add_lifeline("worker", "Worker")
    
    # Add messages
    generator.add_message(
        source="client",
        target="queue",
        message="publishEvent()",
        message_type=MessageType.ASYNCHRONOUS
    )
    generator.add_message(
        source="queue",
        target="worker",
        message="processEvent()",
        message_type=MessageType.ASYNCHRONOUS
    )
    generator.add_message(
        source="worker",
        target="queue",
        message="acknowledge()",
        message_type=MessageType.ASYNCHRONOUS
    )
    
    # Generate diagram
    diagram = generator.generate()
    assert diagram is not None
    assert len(generator.lifelines) == 3
    assert len(generator.messages) == 3
    
    # Verify message types
    for msg in generator.messages:
        assert msg.message_type == MessageType.ASYNCHRONOUS

def test_self_message(generator):
    """Test self-message handling"""
    # Add lifeline
    generator.add_lifeline("service", "Service")
    
    # Add self messages
    generator.add_message(
        source="service",
        target="service",
        message="validateState()",
        message_type=MessageType.SYNCHRONOUS
    )
    generator.add_message(
        source="service",
        target="service",
        message="updateCache()",
        message_type=MessageType.SYNCHRONOUS
    )
    
    # Generate diagram
    diagram = generator.generate()
    assert diagram is not None
    assert len(generator.lifelines) == 1
    assert len(generator.messages) == 2

def test_activation_boxes(generator):
    """Test activation box handling"""
    # Add lifelines
    generator.add_lifeline("controller", "Controller")
    generator.add_lifeline("service", "Service")
    
    # Create activation boxes
    controller_box = ActivationBox(
        lifeline="controller",
        start_time=0,
        end_time=3
    )
    service_box = ActivationBox(
        lifeline="service",
        start_time=1,
        end_time=2
    )
    
    # Add activation boxes
    generator.add_activation_box(controller_box)
    generator.add_activation_box(service_box)
    
    # Add messages within activation periods
    generator.add_message(
        source="controller",
        target="service",
        message="process()",
        message_type=MessageType.SYNCHRONOUS,
        time=1
    )
    generator.add_message(
        source="service",
        target="controller",
        message="return result",
        message_type=MessageType.RETURN,
        time=2
    )
    
    # Generate diagram
    diagram = generator.generate()
    assert diagram is not None
    assert len(generator.activation_boxes) == 2
    assert len(generator.messages) == 2

def test_nested_calls(generator):
    """Test nested method call sequence"""
    # Add lifelines
    generator.add_lifeline("client", "Client")
    generator.add_lifeline("service", "Service")
    generator.add_lifeline("repository", "Repository")
    
    # Add nested call sequence
    generator.add_message(
        source="client",
        target="service",
        message="getData()",
        message_type=MessageType.SYNCHRONOUS
    )
    generator.add_message(
        source="service",
        target="repository",
        message="fetch()",
        message_type=MessageType.SYNCHRONOUS
    )
    generator.add_message(
        source="repository",
        target="service",
        message="return data",
        message_type=MessageType.RETURN
    )
    generator.add_message(
        source="service",
        target="service",
        message="processData()",
        message_type=MessageType.SYNCHRONOUS
    )
    generator.add_message(
        source="service",
        target="client",
        message="return result",
        message_type=MessageType.RETURN
    )
    
    # Generate diagram
    diagram = generator.generate()
    assert diagram is not None
    assert len(generator.lifelines) == 3
    assert len(generator.messages) == 5

def test_create_destroy(generator):
    """Test object creation and destruction"""
    # Add lifelines
    generator.add_lifeline("factory", "Factory")
    generator.add_lifeline("object", "Object", start_time=1)  # Created at time 1
    
    # Add creation message
    generator.add_message(
        source="factory",
        target="object",
        message="create()",
        message_type=MessageType.CREATE,
        time=1
    )
    
    # Add some interactions
    generator.add_message(
        source="factory",
        target="object",
        message="initialize()",
        message_type=MessageType.SYNCHRONOUS,
        time=2
    )
    
    # Add destruction message
    generator.add_message(
        source="factory",
        target="object",
        message="destroy()",
        message_type=MessageType.DESTROY,
        time=3
    )
    
    # Generate diagram
    diagram = generator.generate()
    assert diagram is not None
    assert len(generator.lifelines) == 2
    assert len(generator.messages) == 3

def test_from_operation(generator, model):
    """Test creating sequence diagram from operation"""
    # Create operation with parameters
    operation = Operation(
        name="processOrder",
        parameters=[
            Parameter(name="orderId", param_type="string"),
            Parameter(name="quantity", param_type="int")
        ],
        return_type="OrderResult"
    )
    
    # Generate sequence diagram from operation
    generator.from_operation("OrderService", operation)
    
    # Verify diagram elements
    assert len(generator.lifelines) >= 1
    assert len(generator.messages) >= 1

def test_message_validation(generator):
    """Test message validation"""
    generator.add_lifeline("source", "Source")
    
    # Test invalid source lifeline
    with pytest.raises(ValueError):
        generator.add_message(
            source="nonexistent",
            target="source",
            message="test()",
            message_type=MessageType.SYNCHRONOUS
        )
    
    # Test invalid target lifeline
    with pytest.raises(ValueError):
        generator.add_message(
            source="source",
            target="nonexistent",
            message="test()",
            message_type=MessageType.SYNCHRONOUS
        )
    
    # Test invalid message type
    with pytest.raises(ValueError):
        generator.add_message(
            source="source",
            target="source",
            message="test()",
            message_type="INVALID"
        )

def test_lifeline_validation(generator):
    """Test lifeline validation"""
    # Test duplicate lifeline
    generator.add_lifeline("test", "Test")
    with pytest.raises(ValueError):
        generator.add_lifeline("test", "Test2")
    
    # Test invalid start time
    with pytest.raises(ValueError):
        generator.add_lifeline("test2", "Test2", start_time=-1)
