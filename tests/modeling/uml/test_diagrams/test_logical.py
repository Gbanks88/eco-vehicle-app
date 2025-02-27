"""Tests for the Logical Diagram Generator"""

import pytest
from pathlib import Path
from uuid import uuid4

from src.modeling.uml.core import Model
from src.modeling.uml.diagrams.logical import (
    LogicalDiagramGenerator,
    LogicalElement,
    LogicalRelation,
    ElementType,
    RelationType
)

@pytest.fixture
def model():
    """Create a test model"""
    return Model(name="TestModel")

@pytest.fixture
def generator(model):
    """Create a test diagram generator"""
    return LogicalDiagramGenerator(model)

def test_create_basic_logical(generator):
    """Test basic logical element creation"""
    # Create subsystem
    subsystem = LogicalElement(
        id=str(uuid4()),
        name="OrderManagement",
        element_type=ElementType.SUBSYSTEM,
        responsibilities=["Handle order processing", "Manage order lifecycle"]
    )
    generator.add_element(subsystem)
    
    # Generate diagram
    diagram = generator.generate()
    assert diagram is not None
    assert len(generator.elements) == 1

def test_layered_architecture(generator):
    """Test layered architecture representation"""
    # Create layers
    presentation = LogicalElement(
        id=str(uuid4()),
        name="Presentation Layer",
        element_type=ElementType.LAYER,
        responsibilities=["User interface", "Input validation"]
    )
    business = LogicalElement(
        id=str(uuid4()),
        name="Business Layer",
        element_type=ElementType.LAYER,
        responsibilities=["Business logic", "Domain rules"]
    )
    data = LogicalElement(
        id=str(uuid4()),
        name="Data Layer",
        element_type=ElementType.LAYER,
        responsibilities=["Data access", "Persistence"]
    )
    
    # Add elements
    for layer in [presentation, business, data]:
        generator.add_element(layer)
    
    # Add relations
    generator.add_relation(LogicalRelation(
        source=presentation.id,
        target=business.id,
        type=RelationType.DEPENDS_ON
    ))
    generator.add_relation(LogicalRelation(
        source=business.id,
        target=data.id,
        type=RelationType.DEPENDS_ON
    ))
    
    # Generate diagram
    diagram = generator.generate()
    assert diagram is not None
    assert len(generator.elements) == 3
    assert len(generator.relations) == 2

def test_module_decomposition(generator):
    """Test module decomposition"""
    # Create modules
    auth = LogicalElement(
        id=str(uuid4()),
        name="Authentication",
        element_type=ElementType.MODULE,
        responsibilities=["User authentication", "Session management"]
    )
    order = LogicalElement(
        id=str(uuid4()),
        name="Order Processing",
        element_type=ElementType.MODULE,
        responsibilities=["Order handling", "Inventory check"]
    )
    payment = LogicalElement(
        id=str(uuid4()),
        name="Payment",
        element_type=ElementType.MODULE,
        responsibilities=["Payment processing", "Refund handling"]
    )
    
    # Add modules
    for module in [auth, order, payment]:
        generator.add_element(module)
    
    # Add dependencies
    generator.add_relation(LogicalRelation(
        source=order.id,
        target=auth.id,
        type=RelationType.USES
    ))
    generator.add_relation(LogicalRelation(
        source=order.id,
        target=payment.id,
        type=RelationType.USES
    ))
    
    # Generate diagram
    diagram = generator.generate()
    assert diagram is not None
    assert len(generator.elements) == 3
    assert len(generator.relations) == 2

def test_facade_pattern(generator):
    """Test facade pattern representation"""
    # Create facade
    facade = LogicalElement(
        id=str(uuid4()),
        name="SystemFacade",
        element_type=ElementType.FACADE,
        responsibilities=["Provide unified interface"]
    )
    
    # Create subsystems
    subsystems = []
    for i in range(3):
        subsystem = LogicalElement(
            id=str(uuid4()),
            name=f"Subsystem{i+1}",
            element_type=ElementType.SUBSYSTEM,
            responsibilities=[f"Handle functionality {i+1}"]
        )
        subsystems.append(subsystem)
    
    # Add elements
    generator.add_element(facade)
    for subsystem in subsystems:
        generator.add_element(subsystem)
        generator.add_relation(LogicalRelation(
            source=facade.id,
            target=subsystem.id,
            type=RelationType.DELEGATES_TO
        ))
    
    # Generate diagram
    diagram = generator.generate()
    assert diagram is not None
    assert len(generator.elements) == 4
    assert len(generator.relations) == 3

def test_service_architecture(generator):
    """Test service-oriented architecture"""
    # Create service elements
    gateway = LogicalElement(
        id=str(uuid4()),
        name="API Gateway",
        element_type=ElementType.SERVICE,
        responsibilities=["Route requests", "Authentication"]
    )
    
    services = []
    service_names = ["User", "Order", "Payment", "Inventory"]
    for name in service_names:
        service = LogicalElement(
            id=str(uuid4()),
            name=f"{name}Service",
            element_type=ElementType.SERVICE,
            responsibilities=[f"Handle {name.lower()} operations"]
        )
        services.append(service)
    
    # Add elements
    generator.add_element(gateway)
    for service in services:
        generator.add_element(service)
        generator.add_relation(LogicalRelation(
            source=gateway.id,
            target=service.id,
            type=RelationType.COMMUNICATES_WITH
        ))
    
    # Add inter-service communications
    generator.add_relation(LogicalRelation(
        source=services[1].id,  # OrderService
        target=services[3].id,  # InventoryService
        type=RelationType.USES
    ))
    generator.add_relation(LogicalRelation(
        source=services[1].id,  # OrderService
        target=services[2].id,  # PaymentService
        type=RelationType.USES
    ))
    
    # Generate diagram
    diagram = generator.generate()
    assert diagram is not None
    assert len(generator.elements) == 5
    assert len(generator.relations) == 6

def test_element_validation(generator):
    """Test element validation"""
    # Test duplicate element ID
    element_id = str(uuid4())
    element1 = LogicalElement(
        id=element_id,
        name="Element1",
        element_type=ElementType.MODULE
    )
    element2 = LogicalElement(
        id=element_id,
        name="Element2",
        element_type=ElementType.MODULE
    )
    
    generator.add_element(element1)
    with pytest.raises(ValueError):
        generator.add_element(element2)

def test_relation_validation(generator):
    """Test relation validation"""
    element = LogicalElement(
        id=str(uuid4()),
        name="TestElement",
        element_type=ElementType.MODULE
    )
    generator.add_element(element)
    
    # Test invalid source
    with pytest.raises(ValueError):
        generator.add_relation(LogicalRelation(
            source=str(uuid4()),
            target=element.id,
            type=RelationType.USES
        ))
    
    # Test invalid target
    with pytest.raises(ValueError):
        generator.add_relation(LogicalRelation(
            source=element.id,
            target=str(uuid4()),
            type=RelationType.USES
        ))

def test_responsibility_handling(generator):
    """Test responsibility handling in elements"""
    element = LogicalElement(
        id=str(uuid4()),
        name="TestElement",
        element_type=ElementType.MODULE,
        responsibilities=["Task 1", "Task 2"]
    )
    generator.add_element(element)
    
    # Generate with and without responsibilities
    generator.show_responsibilities = True
    diagram1 = generator.generate()
    generator.show_responsibilities = False
    diagram2 = generator.generate()
    
    assert diagram1 is not None
    assert diagram2 is not None
