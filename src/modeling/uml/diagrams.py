"""
UML diagram generation module
"""
from typing import List, Optional
import graphviz
from .core import Model, Class, Relationship, Package

class DiagramGenerator:
    """Generates UML diagrams using graphviz"""

    def __init__(self, model: Model):
        self.model = model

    def generate_class_diagram(self, package_name: Optional[str] = None) -> graphviz.Digraph:
        """Generate a class diagram"""
        dot = graphviz.Digraph(comment='Class Diagram')
        dot.attr(rankdir='BT')

        # Filter packages if package_name is provided
        packages = [p for p in self.model.packages if not package_name or p.name == package_name]

        # Add classes
        for package in packages:
            with dot.subgraph(name=f'cluster_{package.name}') as p:
                p.attr(label=package.name)
                for element in package.elements:
                    if isinstance(element, Class):
                        # Create class node
                        label = self._create_class_label(element)
                        p.node(str(element.id), label, shape='record')

        # Add relationships
        for rel in self.model.relationships:
            # Style based on relationship type
            if rel.relationship_type == "generalization":
                dot.edge(str(rel.source), str(rel.target), dir='back', arrowhead='empty')
            elif rel.relationship_type == "dependency":
                dot.edge(str(rel.source), str(rel.target), dir='forward', style='dashed')
            else:  # association
                dot.edge(str(rel.source), str(rel.target), dir='none')

        return dot

    def _create_class_label(self, cls: Class) -> str:
        """Create a label for a class node"""
        # Class name compartment
        if cls.is_abstract:
            name = f"{cls.name} [A]"
        else:
            name = cls.name

        # Attributes compartment
        attrs = []
        for attr in cls.attributes:
            visibility = self._get_visibility_symbol(attr.visibility)
            modifiers = []
            if attr.is_static:
                modifiers.append("static")
            if attr.is_final:
                modifiers.append("final")
            modifier_str = " ".join(modifiers)
            if modifier_str:
                modifier_str = f" [{modifier_str}]"
            attrs.append(f"{visibility}{attr.name}: {attr.type}{modifier_str}")

        # Operations compartment
        ops = []
        for op in cls.operations:
            visibility = self._get_visibility_symbol(op.visibility)
            modifiers = []
            if op.is_static:
                modifiers.append("static")
            if op.is_abstract:
                modifiers.append("abstract")
            modifier_str = " ".join(modifiers)
            if modifier_str:
                modifier_str = f" [{modifier_str}]"
            params = ", ".join([f"{p[0]}: {p[1]}" for p in op.parameters])
            return_type = f": {op.return_type}" if op.return_type else ""
            ops.append(f"{visibility}{op.name}({params}){return_type}{modifier_str}")

        # Combine all parts with record format
        parts = [name]
        if attrs:
            parts.append(r"\l".join(attrs) + r"\l")
        else:
            parts.append("")
        if ops:
            parts.append(r"\l".join(ops) + r"\l")
        else:
            parts.append("")
            
        return "{" + "|{" + "}|{".join(parts) + "}}"

    @staticmethod
    def _get_visibility_symbol(visibility: str) -> str:
        """Convert visibility to UML symbol"""
        symbols = {
            "public": "+",
            "private": "-",
            "protected": "#",
            "package": "~"
        }
        return symbols.get(visibility, "+")

class SequenceDiagramGenerator:
    """Generates sequence diagrams"""

    def generate_diagram(self, messages: List[tuple]) -> graphviz.Digraph:
        """Generate a sequence diagram"""
        dot = graphviz.Digraph(comment='Sequence Diagram')
        dot.attr(rankdir='LR')

        # Create participants
        participants = set()
        for msg in messages:
            participants.add(msg[0])
            participants.add(msg[1])

        # Add participant nodes
        for p in participants:
            dot.node(p, p, shape='box')

        # Add message arrows
        for i, (source, target, message) in enumerate(messages):
            dot.edge(source, target, label=message)

        return dot

class StateDiagramGenerator:
    """Generates state diagrams"""

    def generate_diagram(self, states: List[str], transitions: List[tuple]) -> graphviz.Digraph:
        """Generate a state diagram"""
        dot = graphviz.Digraph(comment='State Diagram')
        
        # Add states
        for state in states:
            dot.node(state, state, shape='circle')

        # Add transitions
        for source, target, label in transitions:
            dot.edge(source, target, label=label)

        return dot
