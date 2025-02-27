"""
Deployment diagram generator for UML models.
Visualizes the physical deployment architecture of a system.
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, List, Optional, Set, Union
from uuid import UUID, uuid4

import graphviz
from ..core import Model, Package, Class
from .base import BaseDiagramGenerator, DiagramStyle

class NodeType(Enum):
    """Types of deployment nodes"""
    DEVICE = "device"
    EXECUTION_ENVIRONMENT = "executionEnvironment"
    NODE = "node"
    CONTAINER = "container"
    CLOUD = "cloud"
    DATABASE = "database"
    NETWORK = "network"

class ArtifactType(Enum):
    """Types of deployment artifacts"""
    EXECUTABLE = "executable"
    LIBRARY = "library"
    FILE = "file"
    DATABASE = "database"
    SCRIPT = "script"
    CONFIG = "configuration"
    SERVICE = "service"

@dataclass
class DeploymentNode:
    """Represents a node in a deployment diagram"""
    id: str = field(default_factory=lambda: str(uuid4()))
    name: str
    node_type: NodeType
    stereotype: Optional[str] = None
    properties: Dict[str, str] = field(default_factory=dict)
    artifacts: List['DeploymentArtifact'] = field(default_factory=list)
    subnodes: List['DeploymentNode'] = field(default_factory=list)
    host: Optional[str] = None
    port: Optional[int] = None
    protocol: Optional[str] = None

@dataclass
class DeploymentArtifact:
    """Represents a deployable artifact"""
    id: str = field(default_factory=lambda: str(uuid4()))
    name: str
    artifact_type: ArtifactType
    version: Optional[str] = None
    path: Optional[str] = None
    properties: Dict[str, str] = field(default_factory=dict)

@dataclass
class DeploymentRelation:
    """Represents a relationship between deployment nodes"""
    source: str
    target: str
    relationship_type: str
    stereotype: Optional[str] = None
    bandwidth: Optional[str] = None
    protocol: Optional[str] = None
    properties: Dict[str, str] = field(default_factory=dict)

class DeploymentDiagramGenerator(BaseDiagramGenerator):
    """Generates deployment diagrams"""

    def __init__(self, model: Model, style: Optional[DiagramStyle] = None):
        super().__init__(model, style)
        self.nodes: Dict[str, DeploymentNode] = {}
        self.relations: List[DeploymentRelation] = []
        self.show_properties = True
        self.show_stereotypes = True
        self.show_protocols = True

    def add_node(self, node: DeploymentNode) -> str:
        """Add a deployment node to the diagram"""
        self.nodes[node.id] = node
        return node.id

    def add_relation(self, relation: DeploymentRelation) -> None:
        """Add a relationship between deployment nodes"""
        if relation.source not in self.nodes:
            raise ValueError(f"Source node not found: {relation.source}")
        if relation.target not in self.nodes:
            raise ValueError(f"Target node not found: {relation.target}")
        self.relations.append(relation)

    def _get_node_shape(self, node_type: NodeType) -> str:
        """Get the shape for a node type"""
        shapes = {
            NodeType.DEVICE: "box3d",
            NodeType.EXECUTION_ENVIRONMENT: "component",
            NodeType.NODE: "box3d",
            NodeType.CONTAINER: "box",
            NodeType.CLOUD: "cloud",
            NodeType.DATABASE: "cylinder",
            NodeType.NETWORK: "diamond"
        }
        return shapes.get(node_type, "box")

    def _format_artifact_label(self, artifact: DeploymentArtifact) -> str:
        """Format the label for an artifact"""
        sections = []
        
        # Artifact type and name
        header = [f"<<{artifact.artifact_type.value}>>"]
        if artifact.version:
            header[0] += f" v{artifact.version}"
        sections.append(header)
        
        # Name
        sections.append([artifact.name])
        
        # Properties
        if self.show_properties and artifact.properties:
            prop_section = []
            for key, value in artifact.properties.items():
                prop_section.append(f"{key}: {value}")
            sections.append(prop_section)
        
        return self._create_html_table(
            [section if isinstance(section, list) else [section] for section in sections],
            cellborder='0',
            border='1'
        )

    def _format_node_label(self, node: DeploymentNode) -> str:
        """Format the label for a deployment node"""
        sections = []
        
        # Node type and stereotype
        stereotypes = []
        if self.show_stereotypes and node.stereotype:
            stereotypes.append(node.stereotype)
        stereotypes.append(node.node_type.value)
        sections.append([f"<<{', '.join(stereotypes)}>>"])
        
        # Name with host/port
        name_section = [node.name]
        if self.show_protocols and (node.host or node.port):
            protocol = f"{node.protocol}://" if node.protocol else ""
            host = node.host or "localhost"
            port = f":{node.port}" if node.port else ""
            name_section.append(f"{protocol}{host}{port}")
        sections.append(name_section)
        
        # Properties
        if self.show_properties and node.properties:
            prop_section = []
            for key, value in node.properties.items():
                prop_section.append(f"{key}: {value}")
            sections.append(prop_section)
        
        return self._create_html_table(
            [section if isinstance(section, list) else [section] for section in sections],
            cellborder='0',
            border='1'
        )

    def _add_artifact_node(self, artifact: DeploymentArtifact, parent_id: str) -> str:
        """Add an artifact node to the graph"""
        artifact_id = f"{parent_id}_{artifact.id}"
        
        label = self._format_artifact_label(artifact)
        self._add_node(
            artifact_id,
            label,
            shape="component",
            style="filled",
            fillcolor="white"
        )
        
        return artifact_id

    def _add_deployment_node(self, node: DeploymentNode, parent_graph: Optional[graphviz.Digraph] = None) -> None:
        """Add a deployment node to the graph"""
        graph = parent_graph or self.graph
        
        # Node attributes
        attrs = {
            'shape': self._get_node_shape(node.node_type),
            'style': 'filled',
            'fillcolor': 'white',
            'fontname': self.style.font_name,
            'fontsize': str(self.style.font_size)
        }
        
        # Add label
        label = self._format_node_label(node)
        if label:
            attrs['label'] = label
        
        # Create node
        graph.node(node.id, **attrs)
        
        # Add artifacts
        for artifact in node.artifacts:
            artifact_id = self._add_artifact_node(artifact, node.id)
            self._add_edge(
                node.id,
                artifact_id,
                "",
                style="dashed",
                constraint="false"
            )
        
        # Handle subnodes
        if node.subnodes:
            with graph.subgraph(name=f'cluster_{node.id}') as subgraph:
                subgraph.attr(label="", style='rounded,dashed')
                for subnode in node.subnodes:
                    self._add_deployment_node(subnode, subgraph)

    def generate(self, output_path: Optional[Union[str, Path]] = None, fmt: str = 'png') -> Optional[bytes]:
        """Generate the deployment diagram"""
        self.graph = self._init_graph(
            "deployment_diagram",
            rankdir="TB",
            compound="true",
            splines="ortho"
        )

        # Add all nodes
        for node in self.nodes.values():
            self._add_deployment_node(node)

        # Add all relations
        for relation in self.relations:
            attrs = {
                'fontname': self.style.font_name,
                'fontsize': str(self.style.font_size)
            }
            
            # Style based on relationship type
            if relation.relationship_type == "communication":
                attrs['style'] = 'bold'
            elif relation.relationship_type == "deployment":
                attrs['style'] = 'dashed'
            
            # Add label with protocol and bandwidth
            label_parts = []
            if self.show_stereotypes and relation.stereotype:
                label_parts.append(f"<<{relation.stereotype}>>")
            if self.show_protocols and relation.protocol:
                label_parts.append(relation.protocol)
            if relation.bandwidth:
                label_parts.append(f"{relation.bandwidth}")
            
            if label_parts:
                attrs['label'] = "\\n".join(label_parts)
            
            self._add_edge(relation.source, relation.target, **attrs)

        if output_path:
            self.save(output_path, fmt)
            return None
        
        return self.graph.pipe(format=fmt)

    def from_package(self, package: Package) -> None:
        """Create deployment diagram from a package structure"""
        # Create main node
        main_node = DeploymentNode(
            name=package.name,
            node_type=NodeType.NODE
        )
        main_id = self.add_node(main_node)
        
        # Process classes as artifacts
        for element in package.elements:
            if isinstance(element, Class):
                # Determine artifact type based on class properties
                artifact_type = ArtifactType.SERVICE
                if element.is_interface:
                    artifact_type = ArtifactType.LIBRARY
                elif any(op.name.lower().startswith(("save", "load", "query")) 
                        for op in element.operations):
                    artifact_type = ArtifactType.DATABASE
                
                # Create artifact
                artifact = DeploymentArtifact(
                    name=element.name,
                    artifact_type=artifact_type,
                    properties={
                        "operations": str(len(element.operations)),
                        "attributes": str(len(element.attributes))
                    }
                )
                main_node.artifacts.append(artifact)
        
        # Process subpackages as subnodes
        for subpackage in package.packages:
            subnode = DeploymentNode(
                name=subpackage.name,
                node_type=NodeType.EXECUTION_ENVIRONMENT
            )
            subnode_id = self.add_node(subnode)
            main_node.subnodes.append(subnode)
            
            # Add deployment relation
            self.add_relation(DeploymentRelation(
                source=main_id,
                target=subnode_id,
                relationship_type="deployment"
            ))
