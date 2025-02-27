"""
Sequence diagram generator for UML models.
"""

from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List, Optional, Set, Tuple, Union
from uuid import UUID

import graphviz
from ..core import Model, Class, Operation
from .base import BaseDiagramGenerator, DiagramStyle

@dataclass
class SequenceMessage:
    """Represents a message in a sequence diagram"""
    source: str
    target: str
    message: str
    return_value: Optional[str] = None
    is_async: bool = False
    is_self: bool = False
    activation_level: int = 0
    start_time: Optional[float] = None
    duration: Optional[float] = None
    is_parallel: bool = False
    parallel_group: Optional[str] = None

@dataclass
class Lifeline:
    """Represents a lifeline in a sequence diagram"""
    name: str
    type: str
    messages_sent: List[SequenceMessage] = field(default_factory=list)
    messages_received: List[SequenceMessage] = field(default_factory=list)
    is_actor: bool = False

class SequenceDiagramGenerator(BaseDiagramGenerator):
    """Generates sequence diagrams"""

    def __init__(self, model: Model, style: Optional[DiagramStyle] = None):
        super().__init__(model, style)
        self.lifelines: Dict[str, Lifeline] = {}
        self.messages: List[SequenceMessage] = []
        self.current_y = 0
        self.y_step = 50
        self.activation_x_offset = 5

    def add_lifeline(self, name: str, type_name: str, is_actor: bool = False) -> None:
        """Add a lifeline to the diagram"""
        self.lifelines[name] = Lifeline(name, type_name, is_actor=is_actor)

    def add_message(self, source: str, target: str, message: str,
                   return_value: Optional[str] = None, is_async: bool = False,
                   start_time: Optional[float] = None, duration: Optional[float] = None,
                   is_parallel: bool = False, parallel_group: Optional[str] = None) -> None:
        """Add a message between lifelines"""
        if source not in self.lifelines:
            raise ValueError(f"Source lifeline not found: {source}")
        if target not in self.lifelines:
            raise ValueError(f"Target lifeline not found: {target}")

        msg = SequenceMessage(
            source=source,
            target=target,
            message=message,
            return_value=return_value,
            is_async=is_async,
            is_self=source == target,
            start_time=start_time,
            duration=duration,
            is_parallel=is_parallel,
            parallel_group=parallel_group
        )

        self.messages.append(msg)
        self.lifelines[source].messages_sent.append(msg)
        self.lifelines[target].messages_received.append(msg)

    def _draw_lifeline(self, name: str, x_pos: int) -> None:
        """Draw a lifeline with its activation boxes"""
        lifeline = self.lifelines[name]
        
        # Draw the lifeline box/actor
        box_width = 100
        box_height = 40
        
        if lifeline.is_actor:
            # Draw stick figure for actor
            self._add_node(
                f"actor_{name}",
                f"<<actor>>\n{name}",
                shape="none",
                pos=f"{x_pos},{self.current_y + box_height}!"
            )
        else:
            # Draw object box
            label = self._create_html_table([
                [f":{lifeline.type}" if ":" not in name else name]
            ])
            self._add_node(
                f"object_{name}",
                label,
                shape="box",
                pos=f"{x_pos},{self.current_y + box_height}!"
            )

        # Draw lifeline
        line_start = self.current_y + box_height * 2
        line_end = self.current_y + len(self.messages) * self.y_step + box_height * 3
        
        self.graph.attr('edge', style='dashed', color=self.style.border_color)
        self._add_edge(
            f"object_{name}",
            f"end_{name}",
            '',
            constraint='false',
            style='dashed'
        )
        
        # Draw activation boxes
        activation_levels: Dict[int, Tuple[int, int]] = {}  # level -> (start_y, end_y)
        current_level = 0
        
        for msg in self.messages:
            msg_y = line_start + self.messages.index(msg) * self.y_step
            
            if msg.target == name:
                current_level += 1
                activation_levels[current_level] = (msg_y, None)
            elif msg.source == name and msg.return_value:
                if current_level in activation_levels:
                    start_y, _ = activation_levels[current_level]
                    activation_levels[current_level] = (start_y, msg_y + self.y_step)
                    current_level -= 1

        # Draw the activation boxes
        for level, (start_y, end_y) in activation_levels.items():
            if end_y is None:
                end_y = line_end
            
            box_x = x_pos + level * self.activation_x_offset
            self.graph.node(
                f"activation_{name}_{level}",
                "",
                shape="box",
                style="filled",
                fillcolor=self.style.background_color,
                pos=f"{box_x},{start_y}!",
                width="0.2",
                height=str((end_y - start_y) / 72.0)  # Convert to inches
            )

    def _draw_message(self, msg: SequenceMessage, y_pos: int) -> None:
        """Draw a message arrow between lifelines"""
        source_x = self.lifelines[msg.source].x_pos
        target_x = self.lifelines[msg.target].x_pos
        
        # Determine arrow style
        if msg.is_async:
            arrow = "vee"
            style = "dashed"
        else:
            arrow = "normal"
            style = "solid"
        
        # Draw the message arrow
        if msg.is_self:
            # Self-message (loop)
            control_x = source_x + 50
            self.graph.edge(
                f"object_{msg.source}",
                f"object_{msg.target}",
                msg.message,
                pos=f"{source_x},{y_pos} {control_x},{y_pos+25} {source_x},{y_pos+50}!",
                arrowhead=arrow,
                style=style
            )
        else:
            # Regular message
            self.graph.edge(
                f"object_{msg.source}",
                f"object_{msg.target}",
                msg.message,
                pos=f"{source_x},{y_pos} {target_x},{y_pos}!",
                arrowhead=arrow,
                style=style
            )
        
        # Draw return message if present
        if msg.return_value:
            return_y = y_pos + self.y_step
            self.graph.edge(
                f"object_{msg.target}",
                f"object_{msg.source}",
                msg.return_value,
                pos=f"{target_x},{return_y} {source_x},{return_y}!",
                arrowhead="vee",
                style="dashed"
            )

    def generate(self, output_path: Optional[Union[str, Path]] = None, fmt: str = 'png') -> Optional[bytes]:
        """Generate the sequence diagram"""
        self.graph = self._init_graph(
            "sequence_diagram",
            rankdir="TB",
            ranksep="0.5",
            nodesep="1.0"
        )
        
        # Set up diagram attributes
        self.graph.attr('node', shape='none')
        self.graph.attr('edge', fontsize='10', arrowsize='0.7')
        
        # Create nodes for lifelines
        for name, lifeline in self.lifelines.items():
            label = f"{lifeline.type}\n{name}" if not lifeline.is_actor else f"Actor\n{name}"
            self.graph.node(name, label=label)
        
        # Create message nodes and edges
        for i, msg in enumerate(self.messages):
            # Create invisible nodes for message alignment
            msg_id = f"msg_{i}"
            self.graph.node(msg_id, "", style='invis')
            
            # Create message edge
            edge_attrs = {
                'label': msg.message,
                'style': 'dashed' if msg.is_async else 'solid',
                'arrowhead': 'vee' if msg.is_async else 'normal'
            }
            
            if msg.return_value:
                edge_attrs['label'] += f"\nreturns {msg.return_value}"
                
            if msg.duration is not None:
                edge_attrs['label'] += f"\n({msg.duration}s)"
                
            if msg.parallel_group:
                edge_attrs['color'] = 'blue'
                edge_attrs['label'] += f"\n[{msg.parallel_group}]"
            
            self.graph.edge(msg.source, msg.target, **edge_attrs)

        if output_path:
            self.save(output_path, fmt)
            return None
        
        return self.graph.pipe(format=fmt)

    def from_interaction(self, source_class: str, operation: Operation) -> None:
        """Create sequence diagram from a class operation"""
        # Add the source class as a lifeline
        self.add_lifeline(source_class, source_class)
        
        # Parse operation to extract interactions
        # This is a placeholder - in a real implementation, we would:
        # 1. Parse the operation's code or documentation
        # 2. Extract method calls and their sequence
        # 3. Add corresponding lifelines and messages
        
        # For now, we'll add some example interactions
        target_class = operation.return_type if operation.return_type else "void"
        self.add_lifeline(target_class, target_class)
        
        # Add the operation call
        self.add_message(
            source_class,
            target_class,
            f"{operation.name}({', '.join(p[0] for p in operation.parameters)})",
            return_value=operation.return_type if operation.return_type != "void" else None
        )
