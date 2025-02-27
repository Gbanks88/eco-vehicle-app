"""Tests for the Deployment Diagram Generator"""

import pytest
from pathlib import Path
from uuid import uuid4

from src.modeling.uml.core import Model
from src.modeling.uml.diagrams.deployment import (
    DeploymentDiagramGenerator,
    DeploymentNode,
    DeploymentArtifact,
    DeploymentRelation,
    NodeType,
    RelationType
)

@pytest.fixture
def model():
    """Create a test model"""
    return Model(name="TestModel")

@pytest.fixture
def generator(model):
    """Create a test diagram generator"""
    return DeploymentDiagramGenerator(model)

def test_create_basic_deployment(generator):
    """Test basic deployment node creation"""
    # Create server node
    server = DeploymentNode(
        id=str(uuid4()),
        name="Application Server",
        node_type=NodeType.DEVICE,
        properties={"os": "Linux", "ram": "16GB"}
    )
    generator.add_node(server)
    
    # Add artifact
    app = DeploymentArtifact(
        id=str(uuid4()),
        name="WebApp.war",
        artifact_type="WAR"
    )
    server.add_artifact(app)
    
    # Generate diagram
    diagram = generator.generate()
    assert diagram is not None
    assert len(generator.nodes) == 1
    assert len(server.artifacts) == 1

def test_cloud_deployment(generator):
    """Test cloud deployment scenario"""
    # Create cloud environment
    cloud = DeploymentNode(
        id=str(uuid4()),
        name="AWS Cloud",
        node_type=NodeType.CLOUD,
        properties={"region": "us-west-2"}
    )
    
    # Create EC2 instance
    ec2 = DeploymentNode(
        id=str(uuid4()),
        name="EC2 Instance",
        node_type=NodeType.EXECUTION_ENVIRONMENT,
        properties={"type": "t2.micro"}
    )
    cloud.add_child(ec2)
    
    # Add application artifact
    app = DeploymentArtifact(
        id=str(uuid4()),
        name="microservice.jar",
        artifact_type="JAR"
    )
    ec2.add_artifact(app)
    
    # Add to diagram
    generator.add_node(cloud)
    
    # Generate diagram
    diagram = generator.generate()
    assert diagram is not None
    assert len(generator.nodes) == 1
    assert len(cloud.children) == 1
    assert len(ec2.artifacts) == 1

def test_deployment_relations(generator):
    """Test relations between deployment nodes"""
    # Create nodes
    web_server = DeploymentNode(
        id=str(uuid4()),
        name="Web Server",
        node_type=NodeType.DEVICE
    )
    db_server = DeploymentNode(
        id=str(uuid4()),
        name="Database Server",
        node_type=NodeType.DEVICE
    )
    
    # Add nodes
    generator.add_node(web_server)
    generator.add_node(db_server)
    
    # Create relation
    relation = DeploymentRelation(
        source=web_server.id,
        target=db_server.id,
        type=RelationType.COMMUNICATION_PATH,
        properties={"protocol": "TCP/IP", "port": "5432"}
    )
    generator.add_relation(relation)
    
    # Generate diagram
    diagram = generator.generate()
    assert diagram is not None
    assert len(generator.relations) == 1

def test_complex_deployment(generator):
    """Test complex deployment scenario"""
    # Create load balancer
    lb = DeploymentNode(
        id=str(uuid4()),
        name="Load Balancer",
        node_type=NodeType.DEVICE,
        properties={"type": "nginx"}
    )
    
    # Create application servers
    app_servers = []
    for i in range(2):
        server = DeploymentNode(
            id=str(uuid4()),
            name=f"App Server {i+1}",
            node_type=NodeType.EXECUTION_ENVIRONMENT
        )
        app = DeploymentArtifact(
            id=str(uuid4()),
            name="app.jar",
            artifact_type="JAR"
        )
        server.add_artifact(app)
        app_servers.append(server)
    
    # Create database
    db = DeploymentNode(
        id=str(uuid4()),
        name="Database",
        node_type=NodeType.DEVICE,
        properties={"type": "PostgreSQL"}
    )
    
    # Add all nodes
    generator.add_node(lb)
    for server in app_servers:
        generator.add_node(server)
    generator.add_node(db)
    
    # Add relations
    for server in app_servers:
        # LB to App Server
        generator.add_relation(DeploymentRelation(
            source=lb.id,
            target=server.id,
            type=RelationType.COMMUNICATION_PATH,
            properties={"protocol": "HTTP"}
        ))
        # App Server to DB
        generator.add_relation(DeploymentRelation(
            source=server.id,
            target=db.id,
            type=RelationType.COMMUNICATION_PATH,
            properties={"protocol": "TCP/IP"}
        ))
    
    # Generate diagram
    diagram = generator.generate()
    assert diagram is not None
    assert len(generator.nodes) == 4
    assert len(generator.relations) == 4

def test_nested_environments(generator):
    """Test nested deployment environments"""
    # Create container host
    host = DeploymentNode(
        id=str(uuid4()),
        name="Docker Host",
        node_type=NodeType.DEVICE
    )
    
    # Create container runtime
    docker = DeploymentNode(
        id=str(uuid4()),
        name="Docker Runtime",
        node_type=NodeType.EXECUTION_ENVIRONMENT
    )
    host.add_child(docker)
    
    # Create containers
    containers = []
    for i in range(3):
        container = DeploymentNode(
            id=str(uuid4()),
            name=f"Container {i+1}",
            node_type=NodeType.EXECUTION_ENVIRONMENT,
            properties={"image": f"service{i+1}:latest"}
        )
        docker.add_child(container)
        containers.append(container)
    
    # Add to diagram
    generator.add_node(host)
    
    # Generate diagram
    diagram = generator.generate()
    assert diagram is not None
    assert len(host.children) == 1
    assert len(docker.children) == 3

def test_node_validation(generator):
    """Test node validation"""
    # Test duplicate node ID
    node_id = str(uuid4())
    node1 = DeploymentNode(
        id=node_id,
        name="Node1",
        node_type=NodeType.DEVICE
    )
    node2 = DeploymentNode(
        id=node_id,
        name="Node2",
        node_type=NodeType.DEVICE
    )
    
    generator.add_node(node1)
    with pytest.raises(ValueError):
        generator.add_node(node2)

def test_relation_validation(generator):
    """Test relation validation"""
    node = DeploymentNode(
        id=str(uuid4()),
        name="TestNode",
        node_type=NodeType.DEVICE
    )
    generator.add_node(node)
    
    # Test invalid source
    with pytest.raises(ValueError):
        generator.add_relation(DeploymentRelation(
            source=str(uuid4()),
            target=node.id,
            type=RelationType.COMMUNICATION_PATH
        ))
    
    # Test invalid target
    with pytest.raises(ValueError):
        generator.add_relation(DeploymentRelation(
            source=node.id,
            target=str(uuid4()),
            type=RelationType.COMMUNICATION_PATH
        ))

def test_artifact_validation(generator):
    """Test artifact validation"""
    node = DeploymentNode(
        id=str(uuid4()),
        name="TestNode",
        node_type=NodeType.DEVICE
    )
    
    # Test duplicate artifact
    artifact_id = str(uuid4())
    artifact1 = DeploymentArtifact(
        id=artifact_id,
        name="artifact1",
        artifact_type="JAR"
    )
    artifact2 = DeploymentArtifact(
        id=artifact_id,
        name="artifact2",
        artifact_type="JAR"
    )
    
    node.add_artifact(artifact1)
    with pytest.raises(ValueError):
        node.add_artifact(artifact2)
