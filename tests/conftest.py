"""Global pytest configuration and fixtures"""

import pytest
from pathlib import Path
from typing import Dict, Any, List
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
from src.modeling.uml.diagrams.activity import ActivityDiagramGenerator, ActivityNode, ActivityNodeType
from src.modeling.uml.diagrams.component import ComponentDiagramGenerator, Component
from src.modeling.uml.diagrams.deployment import DeploymentDiagramGenerator, DeploymentNode
from src.modeling.uml.diagrams.logical import LogicalDiagramGenerator, LogicalElement
from src.modeling.uml.diagrams.sequence import SequenceDiagramGenerator
from src.modeling.uml.diagrams.state import StateDiagramGenerator, State, StateType

@pytest.fixture(scope="session")
def test_data_dir(tmp_path_factory) -> Path:
    """Create and return a temporary directory for test data"""
    return tmp_path_factory.mktemp("test_data")

@pytest.fixture
def sample_model() -> Model:
    """Create a sample model with common elements"""
    model = Model(name="TestModel")
    
    # Add packages
    ui_pkg = Package(name="UI")
    service_pkg = Package(name="Service")
    data_pkg = Package(name="Data")
    
    model.add_package(ui_pkg)
    model.add_package(service_pkg)
    model.add_package(data_pkg)
    
    return model

@pytest.fixture
def sample_class() -> Class:
    """Create a sample class with operations"""
    return Class(
        name="TestClass",
        operations=[
            Operation(
                name="operation1",
                parameters=[
                    Parameter(name="param1", param_type="string"),
                    Parameter(name="param2", param_type="int")
                ],
                return_type="bool"
            ),
            Operation(
                name="operation2",
                parameters=[],
                return_type="void"
            )
        ]
    )

@pytest.fixture
def activity_diagram_elements(sample_model) -> Dict[str, Any]:
    """Create common activity diagram elements"""
    generator = ActivityDiagramGenerator(sample_model)
    
    # Create nodes
    start = ActivityNode(id=str(uuid4()), name="Start", node_type=ActivityNodeType.INITIAL)
    action1 = ActivityNode(id=str(uuid4()), name="Action1", node_type=ActivityNodeType.ACTION)
    decision = ActivityNode(id=str(uuid4()), name="Decision", node_type=ActivityNodeType.DECISION)
    action2 = ActivityNode(id=str(uuid4()), name="Action2", node_type=ActivityNodeType.ACTION)
    action3 = ActivityNode(id=str(uuid4()), name="Action3", node_type=ActivityNodeType.ACTION)
    end = ActivityNode(id=str(uuid4()), name="End", node_type=ActivityNodeType.FINAL)
    
    # Add nodes to generator
    for node in [start, action1, decision, action2, action3, end]:
        generator.add_node(node)
    
    return {
        "generator": generator,
        "nodes": {
            "start": start,
            "action1": action1,
            "decision": decision,
            "action2": action2,
            "action3": action3,
            "end": end
        }
    }

@pytest.fixture
def component_diagram_elements(sample_model) -> Dict[str, Any]:
    """Create common component diagram elements"""
    generator = ComponentDiagramGenerator(sample_model)
    
    # Create components
    ui = Component(id=str(uuid4()), name="UI", stereotype="boundary")
    service = Component(id=str(uuid4()), name="Service", stereotype="service")
    repository = Component(id=str(uuid4()), name="Repository", stereotype="repository")
    
    # Add components to generator
    for component in [ui, service, repository]:
        generator.add_component(component)
    
    return {
        "generator": generator,
        "components": {
            "ui": ui,
            "service": service,
            "repository": repository
        }
    }

@pytest.fixture
def deployment_diagram_elements(sample_model) -> Dict[str, Any]:
    """Create common deployment diagram elements"""
    generator = DeploymentDiagramGenerator(sample_model)
    
    # Create nodes
    web_server = DeploymentNode(id=str(uuid4()), name="WebServer", node_type="server")
    app_server = DeploymentNode(id=str(uuid4()), name="AppServer", node_type="server")
    db_server = DeploymentNode(id=str(uuid4()), name="DBServer", node_type="server")
    
    # Add nodes to generator
    for node in [web_server, app_server, db_server]:
        generator.add_node(node)
    
    return {
        "generator": generator,
        "nodes": {
            "web_server": web_server,
            "app_server": app_server,
            "db_server": db_server
        }
    }

@pytest.fixture
def state_diagram_elements(sample_model) -> Dict[str, Any]:
    """Create common state diagram elements"""
    generator = StateDiagramGenerator(sample_model)
    
    # Create states
    initial = State(id=str(uuid4()), name="Initial", state_type=StateType.INITIAL)
    idle = State(id=str(uuid4()), name="Idle", state_type=StateType.NORMAL)
    processing = State(id=str(uuid4()), name="Processing", state_type=StateType.NORMAL)
    final = State(id=str(uuid4()), name="Final", state_type=StateType.FINAL)
    
    # Add states to generator
    for state in [initial, idle, processing, final]:
        generator.add_state(state)
    
    return {
        "generator": generator,
        "states": {
            "initial": initial,
            "idle": idle,
            "processing": processing,
            "final": final
        }
    }

@pytest.fixture
def mock_file_system(test_data_dir) -> Dict[str, Path]:
    """Create a mock file system structure for testing"""
    # Create directories
    src_dir = test_data_dir / "src"
    test_dir = test_data_dir / "tests"
    docs_dir = test_data_dir / "docs"
    
    for dir_path in [src_dir, test_dir, docs_dir]:
        dir_path.mkdir(parents=True, exist_ok=True)
    
    return {
        "root": test_data_dir,
        "src": src_dir,
        "test": test_dir,
        "docs": docs_dir
    }

class DiagramTestHelper:
    """Helper class for diagram testing"""
    
    @staticmethod
    def verify_diagram_elements(diagram: Any, expected_elements: List[Any]) -> bool:
        """Verify that all expected elements exist in the diagram"""
        for element in expected_elements:
            if not diagram.contains_element(element):
                return False
        return True
    
    @staticmethod
    def verify_diagram_connections(diagram: Any, connections: List[tuple]) -> bool:
        """Verify that all expected connections exist in the diagram"""
        for source, target in connections:
            if not diagram.has_connection(source, target):
                return False
        return True
    
    @staticmethod
    def verify_diagram_hierarchy(diagram: Any, hierarchy: Dict[str, List[str]]) -> bool:
        """Verify hierarchical relationships in the diagram"""
        for parent, children in hierarchy.items():
            for child in children:
                if not diagram.is_child_of(child, parent):
                    return False
        return True

@pytest.fixture
def diagram_helper() -> DiagramTestHelper:
    """Provide access to diagram testing helper methods"""
    return DiagramTestHelper
