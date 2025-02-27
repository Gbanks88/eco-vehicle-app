"""
State diagram generator for UML models.
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Set, Union
from uuid import UUID

import graphviz
from ..core import Model, Class, Operation
from .base import BaseDiagramGenerator, DiagramStyle

@dataclass
class State:
    """Represents a state in a state diagram"""
    name: str
    description: Optional[str] = None
    entry_actions: List[str] = field(default_factory=list)
    exit_actions: List[str] = field(default_factory=list)
    do_actions: List[str] = field(default_factory=list)
    is_initial: bool = False
    is_final: bool = False
    is_composite: bool = False
    substates: List['State'] = field(default_factory=list)

@dataclass
class Transition:
    """Represents a transition between states"""
    source: str
    target: str
    trigger: Optional[str] = None
    guard: Optional[str] = None
    action: Optional[str] = None

class StateDiagramGenerator(BaseDiagramGenerator):
    """Generates state diagrams"""

    def __init__(self, model: Model, style: Optional[DiagramStyle] = None):
        super().__init__(model, style)
        self.states: Dict[str, State] = {}
        self.transitions: List[Transition] = []
        self.current_cluster = 0

    def add_state(self, state: State) -> None:
        """Add a state to the diagram"""
        self.states[state.name] = state

    def add_transition(self, transition: Transition) -> None:
        """Add a transition between states"""
        if transition.source not in self.states and not any(s.is_initial for s in self.states.values()):
            raise ValueError(f"Source state not found: {transition.source}")
        if transition.target not in self.states and not any(s.is_final for s in self.states.values()):
            raise ValueError(f"Target state not found: {transition.target}")
        self.transitions.append(transition)

    def _format_state_label(self, state: State) -> str:
        """Format the label for a state node"""
        if state.is_initial:
            return ""
        if state.is_final:
            return ""

        sections = []
        
        # State name
        sections.append([state.name])
        
        # Entry/Exit/Do actions
        internal_actions = []
        if state.entry_actions:
            internal_actions.extend(f"entry / {action}" for action in state.entry_actions)
        if state.exit_actions:
            internal_actions.extend(f"exit / {action}" for action in state.exit_actions)
        if state.do_actions:
            internal_actions.extend(f"do / {action}" for action in state.do_actions)
        
        if internal_actions:
            sections.append(internal_actions)
        
        return self._create_html_table(
            [section if isinstance(section, list) else [section] for section in sections],
            cellborder='0',
            border='1'
        )

    def _add_state_node(self, state: State, parent_graph: Optional[graphviz.Digraph] = None) -> None:
        """Add a state node to the graph"""
        graph = parent_graph or self.graph
        
        if state.is_initial:
            graph.node(
                state.name,
                "",
                shape="circle",
                style="filled",
                fillcolor="black",
                width="0.3",
                height="0.3"
            )
        elif state.is_final:
            graph.node(
                state.name,
                "",
                shape="doublecircle",
                style="filled",
                fillcolor="white",
                width="0.3",
                height="0.3"
            )
        else:
            label = self._format_state_label(state)
            
            if state.is_composite:
                # Create a subgraph for composite state
                self.current_cluster += 1
                with graph.subgraph(name=f'cluster_{self.current_cluster}') as subgraph:
                    subgraph.attr(label=state.name, style='rounded')
                    
                    # Add substates
                    for substate in state.substates:
                        self._add_state_node(substate, subgraph)
            else:
                graph.node(
                    state.name,
                    label,
                    shape="box",
                    style="rounded"
                )

    def _format_transition_label(self, transition: Transition) -> str:
        """Format the label for a transition edge"""
        parts = []
        
        if transition.trigger:
            parts.append(transition.trigger)
        
        if transition.guard:
            parts.append(f"[{transition.guard}]")
            
        if transition.action:
            parts.append(f"/ {transition.action}")
            
        return "\\n".join(parts)

    def generate(self, output_path: Optional[Union[str, Path]] = None, fmt: str = 'png') -> Optional[bytes]:
        """Generate the state diagram"""
        self.graph = self._init_graph(
            "state_diagram",
            rankdir="TB",
            ranksep="0.8",
            nodesep="0.8"
        )

        # Add all states
        for state in self.states.values():
            self._add_state_node(state)

        # Add all transitions
        for transition in self.transitions:
            label = self._format_transition_label(transition)
            
            # Special handling for initial and final transitions
            source_state = self.states.get(transition.source)
            target_state = self.states.get(transition.target)
            
            edge_attrs = {
                'label': label,
                'fontname': self.style.font_name,
                'fontsize': str(self.style.font_size)
            }
            
            if source_state and source_state.is_initial:
                edge_attrs['arrowsize'] = '1.5'
            elif target_state and target_state.is_final:
                edge_attrs['arrowsize'] = '1.5'
            
            self._add_edge(transition.source, transition.target, **edge_attrs)

        if output_path:
            self.save(output_path, fmt)
            return None
        
        return self.graph.pipe(format=fmt)

    def from_class(self, cls: Class) -> None:
        """Create state diagram from a class"""
        # Add initial and final states
        initial_state = State("initial", is_initial=True)
        final_state = State("final", is_final=True)
        self.add_state(initial_state)
        self.add_state(final_state)
        
        # Extract states and transitions from class
        # This is a placeholder - in a real implementation, we would:
        # 1. Analyze class attributes and methods
        # 2. Look for state-related patterns (e.g., state machine implementation)
        # 3. Extract states and transitions
        
        # Example: Create states from class operations
        for operation in cls.operations:
            state = State(
                name=operation.name,
                entry_actions=[f"call {operation.name}"],
                description=operation.description
            )
            self.add_state(state)
            
            # Add transition from previous state or initial
            prev_state = initial_state.name
            self.add_transition(Transition(
                source=prev_state,
                target=state.name,
                trigger=f"invoke_{operation.name}",
                action=f"execute_{operation.name}"
            ))
            
        # Add transition to final state
        self.add_transition(Transition(
            source=list(self.states.keys())[-2],  # Last non-final state
            target=final_state.name,
            trigger="complete"
        ))
