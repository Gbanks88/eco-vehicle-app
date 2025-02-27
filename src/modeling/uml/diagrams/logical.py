"""
Logical diagram generator for UML models.
Focuses on logical architecture and system decomposition.
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, List, Optional, Set, Union
from uuid import UUID, uuid4

import graphviz
from ..core import Model, Package, Class, Relationship
from .base import BaseDiagramGenerator, DiagramStyle

class LogicalElementType(Enum):
    """Types of logical elements"""
    SUBSYSTEM = "subsystem"
    MODULE = "module"
    LAYER = "layer"
    FACADE = "facade"
    SERVICE = "service"
    REPOSITORY = "repository"
    DOMAIN = "domain"
    UTILITY = "utility"

@dataclass
class LogicalElement:
    """Represents a logical element in the architecture"""
    id: str = field(default_factory=lambda: str(uuid4()))
    name: str
    element_type: LogicalElementType
    stereotype: Optional[str] = None
    responsibilities: List[str] = field(default_factory=list)
    dependencies: List[str] = field(default_factory=list)
    subelements: List['LogicalElement'] = field(default_factory=list)
    properties: Dict[str, str] = field(default_factory=dict)
    layer: Optional[int] = None

@dataclass
class LogicalRelation:
    """Represents a relationship between logical elements"""
    source: str
    target: str
    relationship_type: str
    stereotype: Optional[str] = None
    multiplicity: Optional[str] = None
    properties: Dict[str, str] = field(default_factory=dict)

class LogicalDiagramGenerator(BaseDiagramGenerator):
    """Generates logical architecture diagrams"""

    def __init__(self, model: Model, style: Optional[DiagramStyle] = None):
        super().__init__(model, style)
        self.elements: Dict[str, LogicalElement] = {}
        self.relations: List[LogicalRelation] = []
        self.show_responsibilities = True
        self.show_layers = True
        self.current_layer = 0

    def add_element(self, element: LogicalElement) -> str:
        """Add a logical element to the diagram"""
        self.elements[element.id] = element
        return element.id

    def add_relation(self, relation: LogicalRelation) -> None:
        """Add a relationship between logical elements"""
        if relation.source not in self.elements:
            raise ValueError(f"Source element not found: {relation.source}")
        if relation.target not in self.elements:
            raise ValueError(f"Target element not found: {relation.target}")
        self.relations.append(relation)

    def _format_element_label(self, element: LogicalElement) -> str:
        """Format the label for a logical element"""
        sections = []
        
        # Stereotype and type
        stereotypes = []
        if element.stereotype:
            stereotypes.append(element.stereotype)
        stereotypes.append(element.element_type.value)
        sections.append([f"<<{', '.join(stereotypes)}>>"])
        
        # Name
        sections.append([element.name])
        
        # Responsibilities
        if self.show_responsibilities and element.responsibilities:
            resp_section = []
            for resp in element.responsibilities:
                resp_section.append(f"• {resp}")
            sections.append(resp_section)
        
        # Properties
        if element.properties:
            prop_section = []
            for key, value in element.properties.items():
                prop_section.append(f"{key}: {value}")
            sections.append(prop_section)
        
        return self._create_html_table(
            [section if isinstance(section, list) else [section] for section in sections],
            cellborder='0',
            border='1'
        )

    def _add_element_node(self, element: LogicalElement, parent_graph: Optional[graphviz.Digraph] = None) -> None:
        """Add a logical element node to the graph"""
        graph = parent_graph or self.graph
        
        # Element attributes
        attrs = {
            'shape': 'box',
            'style': 'rounded,filled',
            'fillcolor': 'white',
            'fontname': self.style.font_name,
            'fontsize': str(self.style.font_size)
        }
        
        # Special styling for different element types
        if element.element_type == LogicalElementType.LAYER:
            attrs.update({
                'shape': 'box',
                'style': 'filled,striped',
                'fillcolor': f"/spectral9/{element.layer if element.layer is not None else 5}"
            })
        elif element.element_type == LogicalElementType.FACADE:
            attrs.update({
                'shape': 'component',
                'style': 'filled'
            })
        elif element.element_type == LogicalElementType.SERVICE:
            attrs.update({
                'shape': 'hexagon',
                'style': 'filled'
            })
        
        # Add label
        label = self._format_element_label(element)
        if label:
            attrs['label'] = label
        
        # Create element node
        graph.node(element.id, **attrs)
        
        # Handle subelements
        if element.subelements:
            with graph.subgraph(name=f'cluster_{element.id}') as subgraph:
                subgraph.attr(label=element.name, style='rounded,dashed')
                for subelement in element.subelements:
                    self._add_element_node(subelement, subgraph)

    def generate(self, output_path: Optional[Union[str, Path]] = None, fmt: str = 'png') -> Optional[bytes]:
        """Generate the logical diagram"""
        self.graph = self._init_graph(
            "logical_diagram",
            rankdir="TB",
            compound="true",
            splines="ortho"
        )

        # Group elements by layer if enabled
        if self.show_layers:
            layers: Dict[int, List[LogicalElement]] = {}
            standalone_elements = []
            
            for element in self.elements.values():
                if element.layer is not None:
                    if element.layer not in layers:
                        layers[element.layer] = []
                    layers[element.layer].append(element)
                else:
                    standalone_elements.append(element)
            
            # Create subgraphs for each layer
            for layer_num in sorted(layers.keys()):
                with self.graph.subgraph(name=f'cluster_layer_{layer_num}') as subgraph:
                    subgraph.attr(label=f'Layer {layer_num}', style='rounded,dashed')
                    for element in layers[layer_num]:
                        self._add_element_node(element, subgraph)
            
            # Add standalone elements
            for element in standalone_elements:
                self._add_element_node(element)
        else:
            # Add all elements without layers
            for element in self.elements.values():
                self._add_element_node(element)

        # Add all relations
        for relation in self.relations:
            attrs = {
                'fontname': self.style.font_name,
                'fontsize': str(self.style.font_size)
            }
            
            # Style based on relationship type
            if relation.relationship_type == "dependency":
                attrs['style'] = 'dashed'
                attrs['arrowhead'] = 'vee'
            elif relation.relationship_type == "composition":
                attrs['style'] = 'solid'
                attrs['arrowhead'] = 'diamond'
            elif relation.relationship_type == "aggregation":
                attrs['style'] = 'solid'
                attrs['arrowhead'] = 'odiamond'
            
            # Add stereotype and multiplicity if present
            label_parts = []
            if relation.stereotype:
                label_parts.append(f"<<{relation.stereotype}>>")
            if relation.multiplicity:
                label_parts.append(relation.multiplicity)
            
            if label_parts:
                attrs['label'] = "\\n".join(label_parts)
            
            self._add_edge(relation.source, relation.target, **attrs)

        if output_path:
            self.save(output_path, fmt)
            return None
        
        return self.graph.pipe(format=fmt)

    def from_model(self, model: Model) -> None:
        """Create logical diagram from a model"""
        # Create main subsystem
        main_element = LogicalElement(
            name=model.name,
            element_type=LogicalElementType.SUBSYSTEM
        )
        main_id = self.add_element(main_element)
        
        # Process packages as layers
        for i, package in enumerate(model.packages):
            layer_element = LogicalElement(
                name=package.name,
                element_type=LogicalElementType.LAYER,
                layer=i
            )
            layer_id = self.add_element(layer_element)
            
            # Add dependency to main subsystem
            self.add_relation(LogicalRelation(
                source=layer_id,
                target=main_id,
                relationship_type="composition"
            ))
            
            # Process classes in package
            for element in package.elements:
                if isinstance(element, Class):
                    # Determine element type based on class properties
                    element_type = LogicalElementType.SERVICE
                    if element.is_interface:
                        element_type = LogicalElementType.FACADE
                    elif any(op.name.startswith("get") or op.name.startswith("set") 
                            for op in element.operations):
                        element_type = LogicalElementType.REPOSITORY
                    
                    # Create logical element
                    class_element = LogicalElement(
                        name=element.name,
                        element_type=element_type,
                        responsibilities=[op.name for op in element.operations],
                        layer=i
                    )
                    element_id = self.add_element(class_element)
                    
                    # Add dependency to layer
                    self.add_relation(LogicalRelation(
                        source=element_id,
                        target=layer_id,
                        relationship_type="dependency"
                    ))
