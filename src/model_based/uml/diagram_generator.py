"""
UML Diagram Generator Module for Eco-Vehicle Project
Generates UML diagrams for system documentation and analysis
"""

from typing import Dict, Any, List, Optional, Union
import logging
from dataclasses import dataclass
from graphviz import Digraph
import inspect
import ast
from pathlib import Path
import re

logger = logging.getLogger(__name__)

@dataclass
class ClassDefinition:
    """Class definition metadata"""
    name: str
    attributes: List[Dict[str, str]]
    methods: List[Dict[str, str]]
    superclasses: List[str]
    dependencies: List[str]

@dataclass
class SequenceMessage:
    """Message in sequence diagram"""
    source: str
    target: str
    message: str
    response: Optional[str] = None
    is_async: bool = False

class UMLDiagramGenerator:
    """Generates various UML diagrams"""
    
    def __init__(self, config: Dict[str, Any]):
        """
        Initialize UML diagram generator
        
        Args:
            config: Configuration parameters
        """
        self.config = config
        self.output_dir = Path(config.get('output_dir', 'uml_diagrams'))
        self.output_dir.mkdir(exist_ok=True)
        self._setup_logging()
        
    def _setup_logging(self):
        """Configure logging for diagram generator"""
        handler = logging.FileHandler('uml_generator.log')
        handler.setFormatter(logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s'))
        logger.addHandler(handler)
        
    def generate_class_diagram(self,
                             classes: List[Union[str, type]],
                             filename: str) -> str:
        """
        Generate class diagram from list of classes
        
        Args:
            classes: List of class paths or class objects
            filename: Output filename
            
        Returns:
            Path to generated diagram
        """
        try:
            # Create new diagram
            dot = Digraph(comment='Class Diagram')
            dot.attr(rankdir='BT')
            
            # Process each class
            class_definitions = []
            for cls in classes:
                if isinstance(cls, str):
                    # Load class from path
                    class_def = self._extract_class_from_file(cls)
                else:
                    # Extract from class object
                    class_def = self._extract_class_info(cls)
                class_definitions.append(class_def)
                
            # Add classes to diagram
            for class_def in class_definitions:
                self._add_class_to_diagram(dot, class_def)
                
            # Add relationships
            self._add_relationships(dot, class_definitions)
            
            # Save diagram
            output_path = self.output_dir / f"{filename}.png"
            dot.render(str(output_path), format='png', cleanup=True)
            
            logger.info(f"Generated class diagram: {output_path}")
            return str(output_path)
            
        except Exception as e:
            logger.error(f"Error generating class diagram: {str(e)}")
            raise
            
    def generate_sequence_diagram(self,
                                messages: List[SequenceMessage],
                                filename: str) -> str:
        """
        Generate sequence diagram from list of messages
        
        Args:
            messages: List of sequence messages
            filename: Output filename
            
        Returns:
            Path to generated diagram
        """
        try:
            # Create new diagram
            dot = Digraph(comment='Sequence Diagram')
            dot.attr(rankdir='LR')
            
            # Collect all participants
            participants = set()
            for msg in messages:
                participants.add(msg.source)
                participants.add(msg.target)
                
            # Add lifelines
            lifeline_positions = {}
            for i, participant in enumerate(sorted(participants)):
                lifeline_positions[participant] = i
                self._add_lifeline(dot, participant, i)
                
            # Add messages
            for i, msg in enumerate(messages):
                self._add_sequence_message(dot, msg, lifeline_positions, i)
                
            # Save diagram
            output_path = self.output_dir / f"{filename}.png"
            dot.render(str(output_path), format='png', cleanup=True)
            
            logger.info(f"Generated sequence diagram: {output_path}")
            return str(output_path)
            
        except Exception as e:
            logger.error(f"Error generating sequence diagram: {str(e)}")
            raise
            
    def generate_state_diagram(self,
                             states: List[str],
                             transitions: List[Dict[str, Any]],
                             filename: str) -> str:
        """
        Generate state diagram
        
        Args:
            states: List of state names
            transitions: List of state transitions
            filename: Output filename
            
        Returns:
            Path to generated diagram
        """
        try:
            # Create new diagram
            dot = Digraph(comment='State Diagram')
            
            # Add states
            for state in states:
                self._add_state(dot, state)
                
            # Add transitions
            for transition in transitions:
                self._add_transition(dot, transition)
                
            # Save diagram
            output_path = self.output_dir / f"{filename}.png"
            dot.render(str(output_path), format='png', cleanup=True)
            
            logger.info(f"Generated state diagram: {output_path}")
            return str(output_path)
            
        except Exception as e:
            logger.error(f"Error generating state diagram: {str(e)}")
            raise
            
    def _extract_class_from_file(self, file_path: str) -> ClassDefinition:
        """Extract class definition from Python file"""
        with open(file_path, 'r') as f:
            tree = ast.parse(f.read())
            
        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef):
                return self._parse_class_def(node)
                
        raise ValueError(f"No class definition found in {file_path}")
        
    def _extract_class_info(self, cls: type) -> ClassDefinition:
        """Extract class information from class object"""
        attributes = []
        methods = []
        
        # Get attributes and methods
        for name, member in inspect.getmembers(cls):
            if not name.startswith('_'):  # Skip private members
                if inspect.isfunction(member):
                    methods.append({
                        'name': name,
                        'signature': str(inspect.signature(member))
                    })
                else:
                    attributes.append({
                        'name': name,
                        'type': type(member).__name__
                    })
                    
        return ClassDefinition(
            name=cls.__name__,
            attributes=attributes,
            methods=methods,
            superclasses=[base.__name__ for base in cls.__bases__ if base != object],
            dependencies=[]
        )
        
    def _parse_class_def(self, node: ast.ClassDef) -> ClassDefinition:
        """Parse class definition from AST node"""
        attributes = []
        methods = []
        
        for child in node.body:
            if isinstance(child, ast.AnnAssign):
                # Typed attribute
                attributes.append({
                    'name': child.target.id,
                    'type': self._get_type_annotation(child.annotation)
                })
            elif isinstance(child, ast.Assign):
                # Untyped attribute
                for target in child.targets:
                    if isinstance(target, ast.Name):
                        attributes.append({
                            'name': target.id,
                            'type': 'Any'
                        })
            elif isinstance(child, ast.FunctionDef):
                # Method
                methods.append({
                    'name': child.name,
                    'signature': self._get_function_signature(child)
                })
                
        return ClassDefinition(
            name=node.name,
            attributes=attributes,
            methods=methods,
            superclasses=[base.id for base in node.bases],
            dependencies=[]
        )
        
    def _get_type_annotation(self, node: ast.AST) -> str:
        """Get string representation of type annotation"""
        if isinstance(node, ast.Name):
            return node.id
        elif isinstance(node, ast.Subscript):
            return f"{self._get_type_annotation(node.value)}[{self._get_type_annotation(node.slice)}]"
        return 'Any'
        
    def _get_function_signature(self, node: ast.FunctionDef) -> str:
        """Get function signature as string"""
        args = []
        for arg in node.args.args:
            arg_str = arg.arg
            if arg.annotation:
                arg_str += f": {self._get_type_annotation(arg.annotation)}"
            args.append(arg_str)
            
        return f"({', '.join(args)})"
        
    def _add_class_to_diagram(self, dot: Digraph, class_def: ClassDefinition):
        """Add class to diagram"""
        # Create class label
        label = f"{class_def.name}|"
        
        # Add attributes
        label += "\\l".join(f"{attr['name']}: {attr['type']}" for attr in class_def.attributes)
        label += "|"
        
        # Add methods
        label += "\\l".join(f"{method['name']}{method['signature']}" for method in class_def.methods)
        
        # Add class node
        dot.node(class_def.name, label, shape='record')
        
    def _add_relationships(self, dot: Digraph, class_definitions: List[ClassDefinition]):
        """Add relationships between classes"""
        for class_def in class_definitions:
            # Inheritance
            for superclass in class_def.superclasses:
                dot.edge(class_def.name, superclass, arrowhead='empty')
                
            # Dependencies
            for dep in class_def.dependencies:
                dot.edge(class_def.name, dep, style='dashed')
                
    def _add_lifeline(self, dot: Digraph, participant: str, position: int):
        """Add lifeline to sequence diagram"""
        # Add participant box
        dot.node(f"{participant}_box", participant, shape='box')
        
        # Add lifeline
        dot.node(f"{participant}_line", "", shape='none')
        dot.edge(f"{participant}_box", f"{participant}_line", style='dashed')
        
    def _add_sequence_message(self,
                            dot: Digraph,
                            msg: SequenceMessage,
                            positions: Dict[str, int],
                            index: int):
        """Add message to sequence diagram"""
        # Calculate positions
        start_pos = positions[msg.source]
        end_pos = positions[msg.target]
        
        # Add message arrow
        arrow_style = 'dashed' if msg.is_async else 'solid'
        dot.edge(
            f"{msg.source}_line",
            f"{msg.target}_line",
            msg.message,
            style=arrow_style
        )
        
        # Add response if any
        if msg.response:
            dot.edge(
                f"{msg.target}_line",
                f"{msg.source}_line",
                msg.response,
                style='dashed'
            )
            
    def _add_state(self, dot: Digraph, state: str):
        """Add state to state diagram"""
        dot.node(state, state, shape='ellipse')
        
    def _add_transition(self, dot: Digraph, transition: Dict[str, Any]):
        """Add transition to state diagram"""
        dot.edge(
            transition['from'],
            transition['to'],
            transition.get('label', ''),
            style='solid'
        )
