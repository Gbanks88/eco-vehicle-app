"""Integration tests for UML diagram generators"""

import pytest
from pathlib import Path
from uuid import uuid4

from src.modeling.uml.core import (
    Model,
    Package,
    Class,
    Operation,
    Parameter,
    Relationship,
    RelationType
)
from src.modeling.uml.diagrams.activity import ActivityDiagramGenerator
from src.modeling.uml.diagrams.component import ComponentDiagramGenerator
from src.modeling.uml.diagrams.deployment import DeploymentDiagramGenerator
from src.modeling.uml.diagrams.logical import LogicalDiagramGenerator
from src.modeling.uml.diagrams.sequence import SequenceDiagramGenerator
from src.modeling.uml.diagrams.state import StateDiagramGenerator

@pytest.fixture
def model():
    """Create a test model with a complete example system"""
    model = Model(name="ECommerceSystem")
    
    # Create packages
    ui_package = Package(name="UI")
    business_package = Package(name="Business")
    data_package = Package(name="Data")
    
    # Create classes in UI package
    order_controller = Class(
        name="OrderController",
        operations=[
            Operation(
                name="submitOrder",
                parameters=[
                    Parameter(name="orderId", param_type="string"),
                    Parameter(name="items", param_type="List[OrderItem]")
                ],
                return_type="OrderResult"
            )
        ]
    )
    ui_package.add_element(order_controller)
    
    # Create classes in Business package
    order_service = Class(
        name="OrderService",
        operations=[
            Operation(
                name="processOrder",
                parameters=[
                    Parameter(name="order", param_type="Order")
                ],
                return_type="OrderResult"
            ),
            Operation(
                name="validateOrder",
                parameters=[
                    Parameter(name="order", param_type="Order")
                ],
                return_type="bool"
            )
        ]
    )
    business_package.add_element(order_service)
    
    # Create classes in Data package
    order_repository = Class(
        name="OrderRepository",
        operations=[
            Operation(
                name="save",
                parameters=[
                    Parameter(name="order", param_type="Order")
                ],
                return_type="void"
            )
        ]
    )
    data_package.add_element(order_repository)
    
    # Add packages to model
    model.add_package(ui_package)
    model.add_package(business_package)
    model.add_package(data_package)
    
    # Add relationships
    model.add_relationship(Relationship(
        source=order_controller.id,
        target=order_service.id,
        type=RelationType.DEPENDENCY
    ))
    model.add_relationship(Relationship(
        source=order_service.id,
        target=order_repository.id,
        type=RelationType.DEPENDENCY
    ))
    
    return model

def test_component_to_deployment_integration(model):
    """Test integration between component and deployment diagrams"""
    # Generate component diagram
    component_gen = ComponentDiagramGenerator(model)
    component_diagram = component_gen.generate()
    
    # Create deployment diagram based on components
    deployment_gen = DeploymentDiagramGenerator(model)
    
    # Map components to deployment nodes
    for component in component_gen.components.values():
        if "UI" in component.name:
            node_type = "WebServer"
        elif "Service" in component.name:
            node_type = "ApplicationServer"
        else:
            node_type = "DatabaseServer"
            
        deployment_gen.add_node_for_component(component, node_type)
    
    deployment_diagram = deployment_gen.generate()
    
    # Verify integration
    assert len(deployment_gen.nodes) >= len(component_gen.components)
    assert all(node.artifacts for node in deployment_gen.nodes.values())

def test_sequence_to_activity_integration(model):
    """Test integration between sequence and activity diagrams"""
    # Generate sequence diagram for order processing
    sequence_gen = SequenceDiagramGenerator(model)
    sequence_gen.from_operation("OrderService", "processOrder")
    sequence_diagram = sequence_gen.generate()
    
    # Create activity diagram from sequence
    activity_gen = ActivityDiagramGenerator(model)
    activity_gen.from_sequence_diagram(sequence_gen)
    activity_diagram = activity_gen.generate()
    
    # Verify integration
    assert len(activity_gen.nodes) >= len(sequence_gen.messages)
    assert len(activity_gen.edges) >= len(sequence_gen.messages) - 1

def test_state_to_sequence_integration(model):
    """Test integration between state and sequence diagrams"""
    # Generate state diagram for order processing
    state_gen = StateDiagramGenerator(model)
    state_gen.from_class(model.find_element_by_name("Order"))
    state_diagram = state_gen.generate()
    
    # Create sequence diagrams for state transitions
    sequence_gen = SequenceDiagramGenerator(model)
    sequence_diagrams = []
    
    for transition in state_gen.transitions:
        if transition.trigger:
            sequence_gen.from_state_transition(transition)
            sequence_diagrams.append(sequence_gen.generate())
    
    # Verify integration
    assert len(sequence_diagrams) == len([t for t in state_gen.transitions if t.trigger])

def test_logical_to_component_integration(model):
    """Test integration between logical and component diagrams"""
    # Generate logical diagram
    logical_gen = LogicalDiagramGenerator(model)
    logical_diagram = logical_gen.generate()
    
    # Create component diagram from logical elements
    component_gen = ComponentDiagramGenerator(model)
    component_gen.from_logical_diagram(logical_gen)
    component_diagram = component_gen.generate()
    
    # Verify integration
    assert len(component_gen.components) >= len(logical_gen.elements)
    for element in logical_gen.elements.values():
        if element.element_type in ["subsystem", "module"]:
            assert any(c.name == element.name for c in component_gen.components.values())

def test_end_to_end_diagram_generation(model):
    """Test end-to-end generation of all diagram types"""
    # Generate all diagram types
    generators = {
        "component": ComponentDiagramGenerator(model),
        "deployment": DeploymentDiagramGenerator(model),
        "logical": LogicalDiagramGenerator(model),
        "sequence": SequenceDiagramGenerator(model),
        "activity": ActivityDiagramGenerator(model),
        "state": StateDiagramGenerator(model)
    }
    
    diagrams = {}
    for name, generator in generators.items():
        diagrams[name] = generator.generate()
    
    # Verify all diagrams were generated
    assert all(diagram is not None for diagram in diagrams.values())
    
    # Verify cross-references between diagrams
    # Components should be deployed
    assert len(diagrams["deployment"].get_nodes()) >= len(diagrams["component"].get_components())
    
    # Sequence should match activity flow
    assert len(diagrams["sequence"].get_messages()) >= len(diagrams["activity"].get_nodes()) - 2
    
    # Logical structure should be reflected in components
    assert len(diagrams["component"].get_components()) >= len(diagrams["logical"].get_elements())

def test_diagram_consistency(model):
    """Test consistency between different diagram types"""
    # Generate all diagrams
    component_gen = ComponentDiagramGenerator(model)
    deployment_gen = DeploymentDiagramGenerator(model)
    logical_gen = LogicalDiagramGenerator(model)
    
    component_diagram = component_gen.generate()
    deployment_diagram = deployment_gen.generate()
    logical_diagram = logical_gen.generate()
    
    # Verify component interfaces match logical dependencies
    for relation in logical_gen.relations:
        source_component = component_gen.find_component_by_logical_element(relation.source)
        target_component = component_gen.find_component_by_logical_element(relation.target)
        if source_component and target_component:
            assert component_gen.has_interface_between(source_component, target_component)
    
    # Verify deployment matches component structure
    for component in component_gen.components.values():
        node = deployment_gen.find_node_for_component(component)
        assert node is not None
        assert any(a.name == component.name for a in node.artifacts)

def test_diagram_synchronization(model):
    """Test synchronization between diagram updates"""
    # Create initial diagrams
    component_gen = ComponentDiagramGenerator(model)
    deployment_gen = DeploymentDiagramGenerator(model)
    
    initial_component_diagram = component_gen.generate()
    initial_deployment_diagram = deployment_gen.generate()
    
    # Modify component diagram
    new_component = component_gen.add_component("NewService")
    updated_component_diagram = component_gen.generate()
    
    # Synchronize deployment diagram
    deployment_gen.synchronize_with_components(component_gen)
    updated_deployment_diagram = deployment_gen.generate()
    
    # Verify synchronization
    assert len(updated_deployment_diagram.get_nodes()) > len(initial_deployment_diagram.get_nodes())
    assert deployment_gen.find_node_for_component(new_component) is not None
