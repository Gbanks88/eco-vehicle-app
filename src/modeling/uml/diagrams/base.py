"""
Base classes for UML diagram generation.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from enum import Enum
from pathlib import Path
from typing import Dict, List, Optional, Set, Tuple, Union

import graphviz
from ..core import Model, Package, Class, Relationship, UMLElement

class DiagramType(Enum):
    """Types of UML diagrams supported"""
    CLASS = "class"
    SEQUENCE = "sequence"
    ACTIVITY = "activity"
    STATE = "state"
    COMPONENT = "component"
    DEPLOYMENT = "deployment"
    USE_CASE = "use_case"

@dataclass
class DiagramStyle:
    """Style configuration for diagrams"""
    font_name: str = "Arial"
    font_size: int = 10
    node_shape: str = "box"
    node_style: str = "rounded"
    edge_style: str = "solid"
    background_color: str = "white"
    border_color: str = "black"
    text_color: str = "black"
    stereotype_color: str = "#6A8759"
    abstract_color: str = "#A9B7C6"
    interface_color: str = "#CC7832"
    relationship_color: str = "#808080"

class BaseDiagramGenerator(ABC):
    """Base class for all diagram generators"""

    def __init__(self, model: Model, style: Optional[DiagramStyle] = None):
        """Initialize diagram generator"""
        self.model = model
        self.style = style or DiagramStyle()
        self.graph = None
        self.node_map: Dict[str, str] = {}
        self.processed_elements: Set[str] = set()

    def _init_graph(self, name: str, **kwargs) -> graphviz.Digraph:
        """Initialize a new graphviz diagram"""
        graph_attrs = {
            'fontname': self.style.font_name,
            'fontsize': str(self.style.font_size),
            'bgcolor': self.style.background_color,
            'rankdir': 'TB',
            'splines': 'ortho',
            'nodesep': '0.8',
            'ranksep': '1.0',
            'concentrate': 'true'
        }
        graph_attrs.update(kwargs)

        graph = graphviz.Digraph(
            name,
            graph_attr=graph_attrs,
            node_attr={
                'fontname': self.style.font_name,
                'fontsize': str(self.style.font_size),
                'shape': self.style.node_shape,
                'style': self.style.node_style,
                'margin': '0.3,0.1'
            },
            edge_attr={
                'fontname': self.style.font_name,
                'fontsize': str(self.style.font_size),
                'style': self.style.edge_style
            }
        )
        return graph

    def _escape_html(self, text: str) -> str:
        """Escape special characters in HTML labels"""
        return text.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')

    def _format_stereotype(self, stereotype: str) -> str:
        """Format stereotype text"""
        return f'&lt;&lt;{self._escape_html(stereotype)}&gt;&gt;'

    def _get_node_id(self, element: UMLElement) -> str:
        """Get unique node ID for an element"""
        return f"{element.__class__.__name__}_{str(element.id)}"

    def _add_node(self, node_id: str, label: str, **attrs) -> None:
        """Add a node to the graph with given attributes"""
        if not self.graph:
            raise RuntimeError("Graph not initialized")
        
        node_attrs = {
            'label': label,
            'fontname': self.style.font_name,
            'fontsize': str(self.style.font_size)
        }
        node_attrs.update(attrs)
        self.graph.node(node_id, **node_attrs)
        self.node_map[node_id] = label

    def _add_edge(self, source_id: str, target_id: str, label: str = "", **attrs) -> None:
        """Add an edge to the graph with given attributes"""
        if not self.graph:
            raise RuntimeError("Graph not initialized")
        
        edge_attrs = {
            'label': label,
            'fontname': self.style.font_name,
            'fontsize': str(self.style.font_size),
            'color': self.style.relationship_color
        }
        edge_attrs.update(attrs)
        self.graph.edge(source_id, target_id, **edge_attrs)

    @abstractmethod
    def generate(self, output_path: Optional[Union[str, Path]] = None, fmt: str = 'png') -> Optional[bytes]:
        """Generate the diagram"""
        pass

    def _create_html_table(self, rows: List[List[str]], **attrs) -> str:
        """Create an HTML table for node labels"""
        table_attrs = {
            'border': '0',
            'cellborder': '1',
            'cellspacing': '0',
            'cellpadding': '4'
        }
        table_attrs.update(attrs)
        
        attrs_str = ' '.join(f'{k}="{v}"' for k, v in table_attrs.items())
        table = [f'<table {attrs_str}>']
        
        for row in rows:
            table.append('<tr>')
            for cell in row:
                table.append(f'<td>{self._escape_html(cell)}</td>')
            table.append('</tr>')
        
        table.append('</table>')
        return ''.join(table)

    def save(self, output_path: Union[str, Path], fmt: str = 'png') -> None:
        """Save the diagram to a file"""
        if not self.graph:
            raise RuntimeError("No diagram generated yet")
        
        output_path = Path(output_path)
        if not output_path.parent.exists():
            output_path.parent.mkdir(parents=True)
        
        self.graph.render(str(output_path), format=fmt, cleanup=True)

    def get_dot(self) -> str:
        """Get the DOT source of the diagram"""
        if not self.graph:
            raise RuntimeError("No diagram generated yet")
        return self.graph.source

    def _add_subgraph(self, name: str, label: str, **attrs) -> graphviz.Digraph:
        """Add a subgraph to the main graph"""
        if not self.graph:
            raise RuntimeError("Graph not initialized")
        
        subgraph_attrs = {
            'label': label,
            'fontname': self.style.font_name,
            'fontsize': str(self.style.font_size),
            'style': 'rounded',
            'color': self.style.border_color
        }
        subgraph_attrs.update(attrs)
        
        subgraph = graphviz.Digraph(name=f'cluster_{name}')
        for key, value in subgraph_attrs.items():
            subgraph.attr(**{key: str(value)})
        
        return subgraph
