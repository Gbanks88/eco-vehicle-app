"""
Component diagram generator for UML models.
Supports both logical and physical component views.
"""

from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Dict, List, Optional, Set, Union
from uuid import UUID, uuid4

import graphviz
from ..core import Model, Package, Class
from .base import BaseDiagramGenerator, DiagramStyle

class ComponentType(Enum):
    """Types of components"""
    COMPONENT = "component"
    INTERFACE = "interface"
    PORT = "port"
    ARTIFACT = "artifact"
    NODE = "node"
    PACKAGE = "package"
    SUBSYSTEM = "subsystem"

class InterfaceType(Enum):
    """Types of interfaces"""
    PROVIDED = "provided"
    REQUIRED = "required"
    ASSEMBLY = "assembly"
    DELEGATION = "delegation"

@dataclass
class Interface:
    """Represents an interface in a component diagram"""
    id: str = field(default_factory=lambda: str(uuid4()))
    name: str = ""
    interface_type: InterfaceType = InterfaceType.PROVIDED
    operations: List[str] = field(default_factory=list)
    properties: Dict[str, str] = field(default_factory=dict)

@dataclass
class Component:
    """Represents a component in the diagram"""
    name: str
    id: str = field(default_factory=lambda: str(uuid4()))
    component_type: ComponentType = ComponentType.COMPONENT
    stereotype: Optional[str] = None
    provided_interfaces: List[Interface] = field(default_factory=list)
    required_interfaces: List[Interface] = field(default_factory=list)
    subcomponents: List['Component'] = field(default_factory=list)
    properties: Dict[str, str] = field(default_factory=dict)
    is_abstract: bool = False

@dataclass
class ComponentRelation:
    """Represents a relationship between components"""
    source: str
    target: str
    relationship_type: str
    stereotype: Optional[str] = None
    properties: Dict[str, str] = field(default_factory=dict)

class ComponentDiagramGenerator(BaseDiagramGenerator):
    """Generates component diagrams"""

    def __init__(self, model: Model, style: Optional[DiagramStyle] = None):
        super().__init__(model, style)
        self.components: Dict[str, Component] = {}
        self.relations: List[ComponentRelation] = []
        self.show_ports = True
        self.show_interfaces = True
        self.logical_view = True

    def add_component(self, component: Component) -> str:
        """Add a component to the diagram"""
        self.components[component.id] = component
        return component.id

    def add_relation(self, relation: ComponentRelation) -> None:
        """Add a relationship between components"""
        if relation.source not in self.components:
            raise ValueError(f"Source component not found: {relation.source}")
        if relation.target not in self.components:
            raise ValueError(f"Target component not found: {relation.target}")
        self.relations.append(relation)

    def _format_component_label(self, component: Component) -> str:
        """Format the label for a component"""
        sections = []
        
        # Stereotype
        if component.stereotype:
            sections.append([f"<<{component.stereotype}>>"])
        
        # Name
        name_section = [component.name]
        if component.is_abstract:
            name_section[0] = f"<i>{name_section[0]}</i>"
        sections.append(name_section)
        
        # Properties
        if component.properties:
            prop_section = []
            for key, value in component.properties.items():
                prop_section.append(f"{key}: {value}")
            sections.append(prop_section)
        
        return self._create_html_table(
            [section if isinstance(section, list) else [section] for section in sections],
            cellborder='0',
            border='1'
        )

    def _add_interface_node(self, interface: Interface, component_id: str) -> str:
        """Add an interface node to the graph"""
        interface_id = f"{component_id}_{interface.id}"
        
        if interface.interface_type == InterfaceType.PROVIDED:
            # "Lollipop" notation
            self.graph.node(
                interface_id,
                "",
                shape="circle",
                width="0.1",
                height="0.1",
                style="filled",
                fillcolor="black"
            )
        else:
            # "Socket" notation
            self.graph.node(
                interface_id,
                "",
                shape="halfcircle",
                width="0.2",
                height="0.2"
            )
        
        return interface_id

    def _add_component_node(self, component: Component, parent_graph: Optional[graphviz.Digraph] = None) -> None:
        """Add a component node to the graph"""
        graph = parent_graph or self.graph
        
        # Component attributes
        attrs = {
            'shape': 'component' if component.component_type == ComponentType.COMPONENT else 'box',
            'style': 'rounded,filled',
            'fillcolor': 'white',
            'fontname': self.style.font_name,
            'fontsize': str(self.style.font_size)
        }
        
        # Special styling for different component types
        if component.component_type == ComponentType.INTERFACE:
            attrs.update({
                'shape': 'circle',
                'style': 'filled',
                'fillcolor': 'white'
            })
        elif component.component_type == ComponentType.SUBSYSTEM:
            attrs.update({
                'shape': 'folder',
                'style': 'filled'
            })
        
        # Add label
        label = self._format_component_label(component)
        if label:
            attrs['label'] = label
        
        # Create component node
        graph.node(component.id, **attrs)
        
        # Add interfaces if enabled
        if self.show_interfaces:
            for interface in component.provided_interfaces:
                interface_id = self._add_interface_node(interface, component.id)
                self._add_edge(component.id, interface_id, "", style="solid")
            
            for interface in component.required_interfaces:
                interface_id = self._add_interface_node(interface, component.id)
                self._add_edge(interface_id, component.id, "", style="solid")
        
        # Handle subcomponents
        if component.subcomponents:
            with graph.subgraph(name=f'cluster_{component.id}') as subgraph:
                subgraph.attr(label=component.name, style='rounded,dashed')
                for subcomponent in component.subcomponents:
                    self._add_component_node(subcomponent, subgraph)

    def generate(self, output_path: Optional[Union[str, Path]] = None, fmt: str = 'png') -> Optional[bytes]:
        """Generate the component diagram"""
        self.graph = self._init_graph(
            "component_diagram",
            rankdir="TB" if self.logical_view else "LR",
            compound="true",
            splines="ortho"
        )

        # Add all components
        for component in self.components.values():
            self._add_component_node(component)

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
            elif relation.relationship_type == "realization":
                attrs['style'] = 'dashed'
                attrs['arrowhead'] = 'empty'
            elif relation.relationship_type == "assembly":
                attrs['style'] = 'solid'
                attrs['arrowhead'] = 'none'
            
            # Add stereotype if present
            if relation.stereotype:
                attrs['label'] = f"<<{relation.stereotype}>>"
            
            self._add_edge(relation.source, relation.target, **attrs)

        if output_path:
            self.save(output_path, fmt)
            return None
        
        return self.graph.pipe(format=fmt)

    def from_package(self, package: Package) -> None:
        """Create component diagram from a package"""
        # Create main component for package
        main_component = Component(
            name=package.name,
            component_type=ComponentType.SUBSYSTEM,
            stereotype="package"
        )
        main_id = self.add_component(main_component)
        
        # Process classes in package
        for element in package.elements:
            if isinstance(element, Class):
                # Create component for class
                class_component = Component(
                    name=element.name,
                    stereotype="class",
                    is_abstract=element.is_abstract
                )
                
                # Add interfaces
                if element.is_interface:
                    interface = Interface(
                        name=element.name,
                        interface_type=InterfaceType.PROVIDED,
                        operations=[op.name for op in element.operations]
                    )
                    class_component.provided_interfaces.append(interface)
                
                component_id = self.add_component(class_component)
                
                # Add dependency to main package
                self.add_relation(ComponentRelation(
                    source=component_id,
                    target=main_id,
                    relationship_type="dependency"
                ))
        
        # Process subpackages
        for subpackage in package.packages:
            self.from_package(subpackage)
