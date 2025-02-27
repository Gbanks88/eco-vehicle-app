#!/usr/bin/env python3
"""
Demonstration of the Vehicle Modeling System
"""

import sys
from pathlib import Path
import matplotlib.pyplot as plt
import numpy as np

# Add src to Python path
project_root = Path(__file__).resolve().parents[3]
sys.path.append(str(project_root))

from src.modeling.vehicle_model import VehicleModel, MaterialProperties, ComponentSpecs

def load_demo_model():
    """Load and configure a demo vehicle model"""
    # Create materials
    aluminum = MaterialProperties(
        name="Aluminum 6061-T6",
        density=2700,
        yield_strength=276,
        thermal_conductivity=167,
        cost_per_kg=2.5
    )
    
    carbon_fiber = MaterialProperties(
        name="Carbon Fiber Composite",
        density=1600,
        yield_strength=600,
        thermal_conductivity=5,
        cost_per_kg=30.0
    )
    
    # Create model
    model = VehicleModel()
    
    # Add chassis
    chassis = ComponentSpecs(
        name="Main Chassis",
        material=aluminum,
        mass=250,
        dimensions=(4.5, 1.8, 0.15),
        max_stress=200
    )
    model.add_component(chassis)
    
    # Add body panels
    body = ComponentSpecs(
        name="Body Panels",
        material=carbon_fiber,
        mass=120,
        dimensions=(4.6, 1.9, 0.002),
        max_stress=250
    )
    model.add_component(body)
    
    return model

def analyze_model(model):
    """Perform analysis on the vehicle model"""
    print("\n=== Vehicle Model Analysis ===")
    print(f"Total mass: {model.total_mass:.2f} kg")
    print(f"Center of mass: {model.center_of_mass}")
    
    # Analyze each component
    print("\nComponent Analysis:")
    for name, component in model.components.items():
        print(f"\n{name}:")
        print(f"  Material: {component.material.name}")
        print(f"  Mass: {component.mass:.2f} kg")
        print(f"  Volume: {component.dimensions[0] * component.dimensions[1] * component.dimensions[2]:.2f} m³")
        
        # Calculate and check stress under example load
        example_load = 10000  # 10 kN
        stress = model.calculate_stress(name, example_load)
        is_safe = model.check_safety_factor(name, example_load)
        
        print(f"  Stress under {example_load/1000:.1f} kN load: {stress:.2f} MPa")
        print(f"  Safety check: {'PASS' if is_safe else 'FAIL'}")

def visualize_model(model):
    """Create visualizations of the vehicle model"""
    # Plot each component
    for name in model.components:
        print(f"\nVisualizing {name}...")
        model.visualize_component(name)
        plt.show()

def export_results(model):
    """Export model results"""
    output_path = project_root / "outputs" / "modeling" / "vehicle_model.json"
    output_path.parent.mkdir(parents=True, exist_ok=True)
    model.export_model(str(output_path))
    print(f"\nModel exported to: {output_path}")

def main():
    """Main demonstration function"""
    print("=== Eco Vehicle Modeling Demo ===")
    
    # Load model
    print("\nLoading demo model...")
    model = load_demo_model()
    
    # Analyze model
    analyze_model(model)
    
    # Visualize model
    visualize_model(model)
    
    # Export results
    export_results(model)

if __name__ == "__main__":
    main()
