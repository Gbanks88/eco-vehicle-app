"""
Eco Vehicle Modeling System
This module provides a comprehensive set of tools for modeling and analyzing eco-vehicle components.
"""

import numpy as np
import matplotlib.pyplot as plt
from dataclasses import dataclass
from typing import List, Dict, Optional, Tuple
import json
import logging
from pathlib import Path

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class MaterialProperties:
    """Material properties for vehicle components"""
    name: str
    density: float  # kg/m³
    yield_strength: float  # MPa
    thermal_conductivity: float  # W/(m·K)
    cost_per_kg: float  # USD/kg

@dataclass
class ComponentSpecs:
    """Specifications for vehicle components"""
    name: str
    material: MaterialProperties
    mass: float  # kg
    dimensions: Tuple[float, float, float]  # length, width, height in meters
    max_stress: float  # MPa
    safety_factor: float = 1.5

class VehicleModel:
    """Main class for vehicle modeling and analysis"""
    
    def __init__(self, config_path: Optional[str] = None):
        """Initialize the vehicle model"""
        self.components: Dict[str, ComponentSpecs] = {}
        self.total_mass: float = 0.0
        self.center_of_mass: np.ndarray = np.zeros(3)
        
        if config_path:
            self.load_config(config_path)
    
    def load_config(self, config_path: str) -> None:
        """Load configuration from JSON file"""
        try:
            with open(config_path, 'r') as f:
                config = json.load(f)
            logger.info(f"Loaded configuration from {config_path}")
            # Process configuration here
        except Exception as e:
            logger.error(f"Error loading configuration: {e}")
            raise
    
    def add_component(self, component: ComponentSpecs) -> None:
        """Add a component to the vehicle model"""
        self.components[component.name] = component
        self.update_mass_properties()
        logger.info(f"Added component: {component.name}")
    
    def update_mass_properties(self) -> None:
        """Update total mass and center of mass"""
        self.total_mass = sum(comp.mass for comp in self.components.values())
        
        # Calculate center of mass
        com = np.zeros(3)
        for comp in self.components.values():
            com += np.array(comp.dimensions) * comp.mass
        self.center_of_mass = com / self.total_mass if self.total_mass > 0 else com
    
    def calculate_stress(self, component_name: str, load: float) -> float:
        """Calculate stress on a component"""
        if component_name not in self.components:
            raise ValueError(f"Component {component_name} not found")
        
        component = self.components[component_name]
        stress = load / (component.dimensions[0] * component.dimensions[1])
        return stress
    
    def check_safety_factor(self, component_name: str, load: float) -> bool:
        """Check if component meets safety factor under given load"""
        stress = self.calculate_stress(component_name, load)
        component = self.components[component_name]
        return stress * component.safety_factor < component.material.yield_strength
    
    def visualize_component(self, component_name: str) -> None:
        """Visualize a component using matplotlib"""
        if component_name not in self.components:
            raise ValueError(f"Component {component_name} not found")
        
        component = self.components[component_name]
        fig = plt.figure(figsize=(10, 8))
        ax = fig.add_subplot(111, projection='3d')
        
        # Create a simple box representation
        l, w, h = component.dimensions
        x = np.array([0, l, l, 0, 0, l, l, 0])
        y = np.array([0, 0, w, w, 0, 0, w, w])
        z = np.array([0, 0, 0, 0, h, h, h, h])
        
        # Plot vertices
        ax.scatter(x, y, z)
        
        # Plot edges
        for i in range(4):
            ax.plot([x[i], x[i+4]], [y[i], y[i+4]], [z[i], z[i+4]], 'b-')
            ax.plot([x[i], x[(i+1)%4]], [y[i], y[(i+1)%4]], [z[i], z[(i+1)%4]], 'b-')
            ax.plot([x[i+4], x[((i+1)%4)+4]], [y[i+4], y[((i+1)%4)+4]], [z[i+4], z[((i+1)%4)+4]], 'b-')
        
        ax.set_title(f"Component: {component_name}")
        ax.set_xlabel("Length (m)")
        ax.set_ylabel("Width (m)")
        ax.set_zlabel("Height (m)")
        plt.show()
    
    def export_model(self, output_path: str) -> None:
        """Export model data to JSON"""
        model_data = {
            "total_mass": self.total_mass,
            "center_of_mass": self.center_of_mass.tolist(),
            "components": {
                name: {
                    "material": {
                        "name": comp.material.name,
                        "density": comp.material.density,
                        "yield_strength": comp.material.yield_strength,
                        "thermal_conductivity": comp.material.thermal_conductivity,
                        "cost_per_kg": comp.material.cost_per_kg
                    },
                    "mass": comp.mass,
                    "dimensions": comp.dimensions,
                    "max_stress": comp.max_stress,
                    "safety_factor": comp.safety_factor
                }
                for name, comp in self.components.items()
            }
        }
        
        try:
            with open(output_path, 'w') as f:
                json.dump(model_data, f, indent=4)
            logger.info(f"Model exported to {output_path}")
        except Exception as e:
            logger.error(f"Error exporting model: {e}")
            raise

def create_example_model() -> VehicleModel:
    """Create an example vehicle model"""
    # Create material
    aluminum = MaterialProperties(
        name="Aluminum 6061-T6",
        density=2700,  # kg/m³
        yield_strength=276,  # MPa
        thermal_conductivity=167,  # W/(m·K)
        cost_per_kg=2.5  # USD/kg
    )
    
    # Create chassis component
    chassis = ComponentSpecs(
        name="Main Chassis",
        material=aluminum,
        mass=250,  # kg
        dimensions=(4.5, 1.8, 0.15),  # meters
        max_stress=200  # MPa
    )
    
    # Create model and add component
    model = VehicleModel()
    model.add_component(chassis)
    
    return model

if __name__ == "__main__":
    # Create and test example model
    model = create_example_model()
    print(f"Total mass: {model.total_mass:.2f} kg")
    print(f"Center of mass: {model.center_of_mass}")
    
    # Visualize chassis
    model.visualize_component("Main Chassis")
    
    # Export model
    model.export_model("vehicle_model.json")
