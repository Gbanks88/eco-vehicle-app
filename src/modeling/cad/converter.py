"""
CAD conversion and integration utilities.
Handles conversion between different CAD formats and UML model integration.
"""

import os
from pathlib import Path
from typing import Dict, List, Optional, Union
import ezdxf
from ezdxf.document import Drawing
from ezdxf.layouts import Modelspace

class CADConverter:
    """Converts between different CAD formats and integrates with UML models"""
    
    def __init__(self, working_dir: Union[str, Path]):
        self.working_dir = Path(working_dir)
        self.dxf_doc: Optional[Drawing] = None
        self.modelspace: Optional[Modelspace] = None
    
    def load_dxf(self, filename: Union[str, Path]) -> None:
        """Load a DXF file"""
        filepath = self.working_dir / filename
        self.dxf_doc = ezdxf.readfile(filepath)
        self.modelspace = self.dxf_doc.modelspace()
    
    def create_new_dxf(self) -> None:
        """Create a new DXF document"""
        self.dxf_doc = ezdxf.new('R2010')
        self.modelspace = self.dxf_doc.modelspace()
    
    def add_component_geometry(self, 
                             name: str, 
                             position: tuple[float, float], 
                             size: tuple[float, float],
                             component_type: str) -> None:
        """Add a component representation to the CAD drawing"""
        if not self.modelspace:
            raise ValueError("No active document")
            
        # Create component boundary
        x, y = position
        width, height = size
        points = [
            (x, y),
            (x + width, y),
            (x + width, y + height),
            (x, y + height),
            (x, y)
        ]
        
        # Draw component box
        self.modelspace.add_lwpolyline(points)
        
        # Add component name
        self.modelspace.add_text(
            name,
            dxfattribs={
                'height': min(width, height) * 0.1,
                'insert': (x + width/2, y + height/2)
            }
        )
        
        # Add stereotype
        if component_type:
            self.modelspace.add_text(
                f"<<{component_type}>>",
                dxfattribs={
                    'height': min(width, height) * 0.08,
                    'insert': (x + width/2, y + height/2 + min(width, height) * 0.15)
                }
            )
    
    def add_connection(self, 
                      start: tuple[float, float],
                      end: tuple[float, float],
                      connection_type: str) -> None:
        """Add a connection between components"""
        if not self.modelspace:
            raise ValueError("No active document")
            
        # Draw connection line
        self.modelspace.add_line(start, end)
        
        # Add arrow at end
        self._add_arrow(start, end)
        
        # Add connection type label
        mid_x = (start[0] + end[0]) / 2
        mid_y = (start[1] + end[1]) / 2
        self.modelspace.add_text(
            connection_type,
            dxfattribs={
                'height': 2.5,
                'insert': (mid_x, mid_y + 1.5)
            }
        )
    
    def _add_arrow(self, start: tuple[float, float], end: tuple[float, float]) -> None:
        """Add an arrow head at the end point"""
        if not self.modelspace:
            raise ValueError("No active document")
            
        # Calculate arrow points
        dx = end[0] - start[0]
        dy = end[1] - start[1]
        length = (dx*dx + dy*dy) ** 0.5
        if length == 0:
            return
            
        # Normalize direction vector
        dx, dy = dx/length, dy/length
        
        # Arrow properties
        arrow_size = 2.0
        arrow_angle = 0.5  # ~30 degrees
        
        # Calculate arrow points
        ax = dx * arrow_size
        ay = dy * arrow_size
        left = (
            end[0] - ax * cos(arrow_angle) + ay * sin(arrow_angle),
            end[1] - ay * cos(arrow_angle) - ax * sin(arrow_angle)
        )
        right = (
            end[0] - ax * cos(arrow_angle) - ay * sin(arrow_angle),
            end[1] - ay * cos(arrow_angle) + ax * sin(arrow_angle)
        )
        
        # Draw arrow head
        self.modelspace.add_lwpolyline([left, end, right])
    
    def save(self, filename: Union[str, Path]) -> None:
        """Save the current document"""
        if not self.dxf_doc:
            raise ValueError("No active document")
            
        filepath = self.working_dir / filename
        self.dxf_doc.saveas(filepath)
