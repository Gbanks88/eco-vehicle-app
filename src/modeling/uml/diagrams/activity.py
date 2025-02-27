"""
Activity diagram generator for UML models.
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, List, Optional, Set, Union
from uuid import UUID, uuid4

import graphviz
from ..core import Model, Class, Operation
from .base import BaseDiagramGenerator, DiagramStyle

class ActivityNodeType(Enum):
    """Types of activity nodes"""
    INITIAL = "initial"
    FINAL = "final"
    ACTION = "action"
    DECISION = "decision"
    MERGE = "merge"
    FORK = "fork"
    JOIN = "join"
    OBJECT = "object"
    PARTITION = "partition"
    SIGNAL = "signal"
    TIME = "time"

@dataclass
class ActivityNode:
    """Represents a node in an activity diagram"""
    id: str = field(default_factory=lambda: str(uuid4()))
    name: str = ""
    node_type: ActivityNodeType = ActivityNodeType.ACTION
    description: Optional[str] = None
    partition: Optional[str] = None
    is_interrupted: bool = False
    is_structured: bool = False
    subactivities: List['ActivityNode'] = field(default_factory=list)
    metadata: Dict[str, str] = field(default_factory=dict)

@dataclass
class ActivityEdge:
    """Represents an edge in an activity diagram"""
    source: str
    target: str
    guard: Optional[str] = None
    weight: Optional[str] = None
    is_control_flow: bool = True
    is_interrupt: bool = False
    metadata: Dict[str, str] = field(default_factory=dict)

@dataclass
class ActivityPartition:
    """Represents a swimlane/partition in an activity diagram"""
    name: str
    nodes: List[str] = field(default_factory=list)
    subpartitions: List['ActivityPartition'] = field(default_factory=list)

class ActivityDiagramGenerator(BaseDiagramGenerator):
    """Generates activity diagrams"""

    def __init__(self, model: Model, style: Optional[DiagramStyle] = None):
        super().__init__(model, style)
        self.nodes: Dict[str, ActivityNode] = {}
        self.edges: List[ActivityEdge] = []
        self.partitions: List[ActivityPartition] = []
        self.current_partition: Optional[str] = None

    def add_node(self, node: ActivityNode) -> str:
        """Add a node to the diagram"""
        self.nodes[node.id] = node
        if self.current_partition:
            for partition in self.partitions:
                if partition.name == self.current_partition:
                    partition.nodes.append(node.id)
                    break
        return node.id

    def add_edge(self, edge: ActivityEdge) -> None:
        """Add an edge between nodes"""
        if edge.source not in self.nodes:
            raise ValueError(f"Source node not found: {edge.source}")
        if edge.target not in self.nodes:
            raise ValueError(f"Target node not found: {edge.target}")
        self.edges.append(edge)

    def create_partition(self, name: str) -> None:
        """Create a new activity partition (swimlane)"""
        partition = ActivityPartition(name)
        self.partitions.append(partition)
        self.current_partition = name

    def _get_node_shape(self, node_type: ActivityNodeType) -> str:
        """Get the shape for a node type"""
        shapes = {
            ActivityNodeType.INITIAL: "circle",
            ActivityNodeType.FINAL: "doublecircle",
            ActivityNodeType.ACTION: "box",
            ActivityNodeType.DECISION: "diamond",
            ActivityNodeType.MERGE: "diamond",
            ActivityNodeType.FORK: "rect",
            ActivityNodeType.JOIN: "rect",
            ActivityNodeType.OBJECT: "box",
            ActivityNodeType.SIGNAL: "polygon",
            ActivityNodeType.TIME: "box"
        }
        return shapes.get(node_type, "box")

    def _format_node_label(self, node: ActivityNode) -> str:
        """Format the label for an activity node"""
        if node.node_type in {ActivityNodeType.INITIAL, ActivityNodeType.FINAL}:
            return ""
        
        sections = []
        
        # Node name/description
        if node.description:
            sections.append([f"{node.name}\\n{node.description}"])
        else:
            sections.append([node.name])
        
        # Add metadata if present
        if node.metadata:
            metadata_section = []
            for key, value in node.metadata.items():
                metadata_section.append(f"{key}: {value}")
            if metadata_section:
                sections.append(metadata_section)
        
        return self._create_html_table(
            [section if isinstance(section, list) else [section] for section in sections],
            cellborder='0',
            border='1'
        )

    def _add_node_to_graph(self, node: ActivityNode, subgraph: Optional[graphviz.Digraph] = None) -> None:
        """Add a node to the graph or subgraph"""
        graph = subgraph or self.graph
        
        # Node attributes
        attrs = {
            'shape': self._get_node_shape(node.node_type),
            'style': 'rounded,filled' if node.node_type == ActivityNodeType.ACTION else 'filled',
            'fillcolor': 'white',
            'fontname': self.style.font_name,
            'fontsize': str(self.style.font_size)
        }
        
        # Special styling for different node types
        if node.node_type == ActivityNodeType.INITIAL:
            attrs.update({
                'fillcolor': 'black',
                'width': '0.3',
                'height': '0.3'
            })
        elif node.node_type == ActivityNodeType.FINAL:
            attrs.update({
                'fillcolor': 'white',
                'width': '0.3',
                'height': '0.3'
            })
        elif node.node_type == ActivityNodeType.FORK or node.node_type == ActivityNodeType.JOIN:
            attrs.update({
                'shape': 'rect',
                'width': '0.1',
                'height': '2'
            })
        elif node.node_type == ActivityNodeType.SIGNAL:
            attrs.update({
                'shape': 'polygon',
                'sides': '5',
                'peripheries': '2'
            })
        
        # Add label
        label = self._format_node_label(node)
        if label:
            attrs['label'] = label
        
        # Create node
        graph.node(node.id, **attrs)
        
        # Handle structured activities (subactivities)
        if node.is_structured and node.subactivities:
            with graph.subgraph(name=f'cluster_{node.id}') as subgraph:
                subgraph.attr(label=node.name, style='rounded,dashed')
                for subnode in node.subactivities:
                    self._add_node_to_graph(subnode, subgraph)

    def _format_edge_label(self, edge: ActivityEdge) -> str:
        """Format the label for an activity edge"""
        parts = []
        
        if edge.guard:
            parts.append(f"[{edge.guard}]")
        if edge.weight:
            parts.append(f"{{{edge.weight}}}")
            
        return "\\n".join(parts)

    def generate(self, output_path: Optional[Union[str, Path]] = None, fmt: str = 'png') -> Optional[bytes]:
        """Generate the activity diagram"""
        self.graph = self._init_graph(
            "activity_diagram",
            rankdir="TB",
            compound="true"
        )

        # Create partitions if present
        if self.partitions:
            for partition in self.partitions:
                with self.graph.subgraph(name=f'cluster_{partition.name}') as subgraph:
                    subgraph.attr(label=partition.name, style='rounded,dashed')
                    for node_id in partition.nodes:
                        self._add_node_to_graph(self.nodes[node_id], subgraph)
        else:
            # Add all nodes without partitions
            for node in self.nodes.values():
                self._add_node_to_graph(node)

        # Add all edges
        for edge in self.edges:
            attrs = {
                'fontname': self.style.font_name,
                'fontsize': str(self.style.font_size)
            }
            
            # Style based on edge type
            if not edge.is_control_flow:
                attrs['style'] = 'dashed'
            if edge.is_interrupt:
                attrs['style'] = 'dotted'
                attrs['color'] = 'red'
            
            # Add label if present
            label = self._format_edge_label(edge)
            if label:
                attrs['label'] = label
            
            self._add_edge(edge.source, edge.target, **attrs)

        if output_path:
            self.save(output_path, fmt)
            return None
        
        return self.graph.pipe(format=fmt)

    def from_operation(self, operation: Operation) -> None:
        """Create activity diagram from an operation"""
        # Create initial and final nodes
        initial_node = ActivityNode(
            name="Start",
            node_type=ActivityNodeType.INITIAL
        )
        final_node = ActivityNode(
            name="End",
            node_type=ActivityNodeType.FINAL
        )
        
        self.add_node(initial_node)
        self.add_node(final_node)
        
        # Create main action node for operation
        main_action = ActivityNode(
            name=operation.name,
            description=operation.description,
            node_type=ActivityNodeType.ACTION,
            metadata={
                "visibility": operation.visibility,
                "return_type": operation.return_type or "void"
            }
        )
        main_action_id = self.add_node(main_action)
        
        # Add edge from initial to main action
        self.add_edge(ActivityEdge(
            source=initial_node.id,
            target=main_action_id
        ))
        
        # Add parameters as object nodes
        prev_node_id = main_action_id
        for param_name, param_type in operation.parameters:
            param_node = ActivityNode(
                name=param_name,
                node_type=ActivityNodeType.OBJECT,
                metadata={"type": param_type}
            )
            param_id = self.add_node(param_node)
            
            # Connect parameter to action
            self.add_edge(ActivityEdge(
                source=prev_node_id,
                target=param_id,
                is_control_flow=False
            ))
            
            prev_node_id = param_id
        
        # Connect last node to final
        self.add_edge(ActivityEdge(
            source=prev_node_id,
            target=final_node.id
        ))
