"""Tests for the Component Diagram Generator"""

import pytest
from pathlib import Path
from uuid import uuid4

from src.modeling.uml.core import Model, Package
from src.modeling.uml.diagrams.component import (
    ComponentDiagramGenerator,
    Component,
    Interface,
    Port,
    ComponentRelation,
    RelationType
)

@pytest.fixture
def model():
    """Create a test model"""
    return Model(name="TestModel")

@pytest.fixture
def generator(model):
    """Create a test diagram generator"""
    return ComponentDiagramGenerator(model)

def test_create_basic_component(generator):
    """Test basic component creation"""
    # Create component
    comp = Component(
        id=str(uuid4()),
        name="OrderProcessor",
        stereotype="service"
    )
    generator.add_component(comp)
    
    # Generate diagram
    diagram = generator.generate()
    assert diagram is not None
    assert len(generator.components) == 1
    assert comp.id in generator.components

def test_component_with_interfaces(generator):
    """Test component with provided and required interfaces"""
    # Create components
    order_processor = Component(
        id=str(uuid4()),
        name="OrderProcessor",
        stereotype="service"
    )
    
    # Create interfaces
    order_interface = Interface(
        id=str(uuid4()),
        name="IOrderProcessing",
        provided=True
    )
    db_interface = Interface(
        id=str(uuid4()),
        name="IDatabase",
        provided=False
    )
    
    # Add interfaces to component
    order_processor.add_interface(order_interface)
    order_processor.add_interface(db_interface)
    
    # Add to diagram
    generator.add_component(order_processor)
    
    # Generate diagram
    diagram = generator.generate()
    assert diagram is not None
    assert len(order_processor.interfaces) == 2

def test_component_relations(generator):
    """Test relations between components"""
    # Create components
    comp1 = Component(id=str(uuid4()), name="WebUI")
    comp2 = Component(id=str(uuid4()), name="Backend")
    
    # Add components
    generator.add_component(comp1)
    generator.add_component(comp2)
    
    # Create relation
    relation = ComponentRelation(
        source=comp1.id,
        target=comp2.id,
        type=RelationType.DEPENDENCY,
        label="uses"
    )
    generator.add_relation(relation)
    
    # Generate diagram
    diagram = generator.generate()
    assert diagram is not None
    assert len(generator.relations) == 1

def test_nested_components(generator):
    """Test nested component structure"""
    # Create parent component
    parent = Component(
        id=str(uuid4()),
        name="System",
        stereotype="subsystem"
    )
    
    # Create child components
    child1 = Component(id=str(uuid4()), name="Frontend")
    child2 = Component(id=str(uuid4()), name="Backend")
    
    # Add children to parent
    parent.add_child(child1)
    parent.add_child(child2)
    
    # Add to diagram
    generator.add_component(parent)
    
    # Generate diagram
    diagram = generator.generate()
    assert diagram is not None
    assert len(parent.children) == 2

def test_ports_and_interfaces(generator):
    """Test components with ports and interfaces"""
    # Create component
    comp = Component(id=str(uuid4()), name="ServiceComponent")
    
    # Create ports
    input_port = Port(
        id=str(uuid4()),
        name="input",
        interfaces=[
            Interface(id=str(uuid4()), name="IInput", provided=True)
        ]
    )
    output_port = Port(
        id=str(uuid4()),
        name="output",
        interfaces=[
            Interface(id=str(uuid4()), name="IOutput", provided=False)
        ]
    )
    
    # Add ports to component
    comp.add_port(input_port)
    comp.add_port(output_port)
    
    # Add to diagram
    generator.add_component(comp)
    
    # Generate diagram
    diagram = generator.generate()
    assert diagram is not None
    assert len(comp.ports) == 2

def test_component_validation(generator):
    """Test component validation"""
    # Test duplicate component
    comp_id = str(uuid4())
    comp1 = Component(id=comp_id, name="Comp1")
    comp2 = Component(id=comp_id, name="Comp2")
    
    generator.add_component(comp1)
    with pytest.raises(ValueError):
        generator.add_component(comp2)

def test_relation_validation(generator):
    """Test relation validation"""
    comp = Component(id=str(uuid4()), name="TestComp")
    generator.add_component(comp)
    
    # Test invalid source
    with pytest.raises(ValueError):
        generator.add_relation(ComponentRelation(
            source=str(uuid4()),
            target=comp.id,
            type=RelationType.DEPENDENCY
        ))
    
    # Test invalid target
    with pytest.raises(ValueError):
        generator.add_relation(ComponentRelation(
            source=comp.id,
            target=str(uuid4()),
            type=RelationType.DEPENDENCY
        ))

def test_from_package(generator, model):
    """Test creating component diagram from package"""
    # Create package with components
    package = Package(name="TestPackage")
    comp1 = Component(id=str(uuid4()), name="Comp1")
    comp2 = Component(id=str(uuid4()), name="Comp2")
    
    package.add_element(comp1)
    package.add_element(comp2)
    model.add_package(package)
    
    # Generate diagram from package
    generator.from_package(package)
    
    assert len(generator.components) == 2
