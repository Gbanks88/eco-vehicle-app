"""
Integrates UML models with CAD representations.
Provides bidirectional mapping between software components and physical parts.
"""

from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List, Optional, Set, Union
from uuid import UUID, uuid4

from ..uml.core import Model
from ..uml.diagrams.component import Component, ComponentDiagramGenerator
from ..uml.diagrams.sequence import SequenceDiagramGenerator
from ..cad.converter import CADConverter

@dataclass
class PhysicalComponent:
    """Represents a physical component in the system"""
    name: str
    id: str = field(default_factory=lambda: str(uuid4()))
    cad_file: Optional[str] = None
    dimensions: tuple[float, float, float] = (0, 0, 0)
    mass: float = 0.0
    material: str = ""
    properties: Dict[str, str] = field(default_factory=dict)

@dataclass
class ComponentMapping:
    """Maps between software components and physical parts"""
    software_component: Component
    physical_component: PhysicalComponent
    relationship_type: str = "implements"
    properties: Dict[str, str] = field(default_factory=dict)

class ModelIntegrator:
    """Integrates software models with physical components"""
    
    def __init__(self, model: Model, cad_dir: Union[str, Path]):
        self.model = model
        self.cad_dir = Path(cad_dir)
        self.physical_components: Dict[str, PhysicalComponent] = {}
        self.mappings: List[ComponentMapping] = []
        self.cad_converter = CADConverter(cad_dir)
        
    def add_physical_component(self, component: PhysicalComponent) -> str:
        """Add a physical component to the system"""
        self.physical_components[component.id] = component
        return component.id
        
    def add_mapping(self, mapping: ComponentMapping) -> None:
        """Add a mapping between software and physical components"""
        if mapping.software_component.id not in self.model.components:
            raise ValueError(f"Software component not found: {mapping.software_component.name}")
        if mapping.physical_component.id not in self.physical_components:
            raise ValueError(f"Physical component not found: {mapping.physical_component.name}")
        self.mappings.append(mapping)
        
    def generate_integrated_diagram(self, output_file: str) -> None:
        """Generate an integrated diagram showing both software and physical components"""
        self.cad_converter.create_new_dxf()
        
        # Layout settings
        margin = 10
        component_width = 40
        component_height = 20
        spacing = 30
        
        # Add software components
        y_pos = margin
        for comp_id, component in self.model.components.items():
            self.cad_converter.add_component_geometry(
                name=component.name,
                position=(margin, y_pos),
                size=(component_width, component_height),
                component_type="software"
            )
            y_pos += component_height + spacing
            
        # Add physical components
        y_pos = margin
        x_pos = margin + component_width + spacing * 2
        for comp_id, component in self.physical_components.items():
            self.cad_converter.add_component_geometry(
                name=component.name,
                position=(x_pos, y_pos),
                size=(component_width, component_height),
                component_type="physical"
            )
            y_pos += component_height + spacing
            
        # Add mappings
        for mapping in self.mappings:
            sw_comp = mapping.software_component
            ph_comp = mapping.physical_component
            
            # Calculate connection points
            sw_x = margin + component_width
            sw_y = margin + component_height/2
            ph_x = x_pos
            ph_y = margin + component_height/2
            
            self.cad_converter.add_connection(
                start=(sw_x, sw_y),
                end=(ph_x, ph_y),
                connection_type=mapping.relationship_type
            )
        
        self.cad_converter.save(output_file)
        
    def validate_design(self) -> List[str]:
        """Validate the integrated design"""
        warnings = []
        
        # Check for unmapped software components
        mapped_sw_components = {m.software_component.id for m in self.mappings}
        for comp_id, component in self.model.components.items():
            if comp_id not in mapped_sw_components:
                warnings.append(f"Software component not mapped to physical part: {component.name}")
        
        # Check for unmapped physical components
        mapped_ph_components = {m.physical_component.id for m in self.mappings}
        for comp_id, component in self.physical_components.items():
            if comp_id not in mapped_ph_components:
                warnings.append(f"Physical component not mapped to software: {component.name}")
        
        # Check for missing CAD files
        for component in self.physical_components.values():
            if component.cad_file:
                cad_path = self.cad_dir / component.cad_file
                if not cad_path.exists():
                    warnings.append(f"CAD file not found for component {component.name}: {component.cad_file}")
        
        return warnings
