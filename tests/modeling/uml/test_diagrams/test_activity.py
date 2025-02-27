"""Tests for the Activity Diagram Generator"""

import pytest
from pathlib import Path
from uuid import uuid4
from datetime import datetime

from src.modeling.uml.core import Model
from src.modeling.uml.diagrams.activity import (
    ActivityDiagramGenerator,
    ActivityNode,
    ActivityEdge,
    ActivityNodeType,
    ActivityPartition
)

@pytest.fixture
def model():
    """Create a test model"""
    return Model(name="TestModel")

@pytest.fixture
def generator(model):
    """Create a test diagram generator"""
    return ActivityDiagramGenerator(model)

def test_create_activity_diagram(generator):
    """Test basic activity diagram creation"""
    # Add initial node
    initial = ActivityNode(
        id=str(uuid4()),
        name="Start",
        node_type=ActivityNodeType.INITIAL
    )
    generator.add_node(initial)
    
    # Add action node
    action = ActivityNode(
        id=str(uuid4()),
        name="Process Order",
        node_type=ActivityNodeType.ACTION
    )
    generator.add_node(action)
    
    # Add decision node
    decision = ActivityNode(
        id=str(uuid4()),
        name="Check Stock",
        node_type=ActivityNodeType.DECISION
    )
    generator.add_node(decision)
    
    # Add final node
    final = ActivityNode(
        id=str(uuid4()),
        name="End",
        node_type=ActivityNodeType.FINAL
    )
    generator.add_node(final)
    
    # Add edges
    generator.add_edge(ActivityEdge(
        source=initial.id,
        target=action.id
    ))
    generator.add_edge(ActivityEdge(
        source=action.id,
        target=decision.id
    ))
    generator.add_edge(ActivityEdge(
        source=decision.id,
        target=final.id,
        guard="[in stock]"
    ))
    
    # Generate diagram
    diagram = generator.generate()
    assert diagram is not None
    assert len(generator.nodes) == 4
    assert len(generator.edges) == 3

def test_activity_partitions(generator):
    """Test activity partitions (swimlanes)"""
    # Create partitions
    generator.create_partition("Sales")
    generator.create_partition("Warehouse")
    
    # Add nodes to partitions
    with generator.current_partition_context("Sales"):
        order_node = ActivityNode(
            id=str(uuid4()),
            name="Receive Order",
            node_type=ActivityNodeType.ACTION
        )
        generator.add_node(order_node)
    
    with generator.current_partition_context("Warehouse"):
        ship_node = ActivityNode(
            id=str(uuid4()),
            name="Ship Order",
            node_type=ActivityNodeType.ACTION
        )
        generator.add_node(ship_node)
    
    # Add edge between partitions
    generator.add_edge(ActivityEdge(
        source=order_node.id,
        target=ship_node.id
    ))
    
    # Generate diagram
    diagram = generator.generate()
    assert diagram is not None
    assert len(generator.partitions) == 2
    assert len(generator.nodes) == 2
    assert len(generator.edges) == 1

def test_complex_activity_flow(generator):
    """Test complex activity flow with various node types"""
    # Create nodes
    start = ActivityNode(id=str(uuid4()), name="Start", node_type=ActivityNodeType.INITIAL)
    fork = ActivityNode(id=str(uuid4()), name="Fork", node_type=ActivityNodeType.FORK)
    action1 = ActivityNode(id=str(uuid4()), name="Validate", node_type=ActivityNodeType.ACTION)
    action2 = ActivityNode(id=str(uuid4()), name="Process", node_type=ActivityNodeType.ACTION)
    join = ActivityNode(id=str(uuid4()), name="Join", node_type=ActivityNodeType.JOIN)
    end = ActivityNode(id=str(uuid4()), name="End", node_type=ActivityNodeType.FINAL)
    
    # Add nodes
    for node in [start, fork, action1, action2, join, end]:
        generator.add_node(node)
    
    # Add edges
    edges = [
        (start.id, fork.id),
        (fork.id, action1.id),
        (fork.id, action2.id),
        (action1.id, join.id),
        (action2.id, join.id),
        (join.id, end.id)
    ]
    
    for source, target in edges:
        generator.add_edge(ActivityEdge(source=source, target=target))
    
    # Generate diagram
    diagram = generator.generate()
    assert diagram is not None
    assert len(generator.nodes) == 6
    assert len(generator.edges) == 6

def test_node_validation(generator):
    """Test node validation"""
    # Test invalid node type
    with pytest.raises(ValueError):
        generator.add_node(ActivityNode(
            id=str(uuid4()),
            name="Invalid",
            node_type="INVALID_TYPE"
        ))
    
    # Test duplicate node ID
    node_id = str(uuid4())
    generator.add_node(ActivityNode(
        id=node_id,
        name="First",
        node_type=ActivityNodeType.ACTION
    ))
    
    with pytest.raises(ValueError):
        generator.add_node(ActivityNode(
            id=node_id,
            name="Second",
            node_type=ActivityNodeType.ACTION
        ))

def test_edge_validation(generator):
    """Test edge validation"""
    node1 = ActivityNode(id=str(uuid4()), name="Node1", node_type=ActivityNodeType.ACTION)
    node2 = ActivityNode(id=str(uuid4()), name="Node2", node_type=ActivityNodeType.ACTION)
    generator.add_node(node1)
    
    # Test edge with non-existent target
    with pytest.raises(ValueError):
        generator.add_edge(ActivityEdge(
            source=node1.id,
            target=node2.id
        ))
    
    # Test edge with non-existent source
    with pytest.raises(ValueError):
        generator.add_edge(ActivityEdge(
            source=str(uuid4()),
            target=node1.id
        ))

def test_partition_validation(generator):
    """Test partition validation"""
    # Test duplicate partition name
    generator.create_partition("Test")
    with pytest.raises(ValueError):
        generator.create_partition("Test")
    
    # Test invalid partition context
    with pytest.raises(ValueError):
        with generator.current_partition_context("NonExistent"):
            pass
