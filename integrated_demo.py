"""
Integrated demo showing UML modeling, CAD integration, and physical-software mapping.
"""

from datetime import datetime
from pathlib import Path
from src.modeling.uml.core import Model, Class, Operation
from src.modeling.uml.diagrams.sequence import SequenceDiagramGenerator
from src.modeling.uml.diagrams.component import (
    Component, ComponentDiagramGenerator, ComponentRelation
)
from src.modeling.cad.converter import CADConverter
from src.modeling.integration.model_integrator import (
    ModelIntegrator, PhysicalComponent, ComponentMapping
)
from src.modeling.agile.process_monitor import AgileProcessMonitor, AgileMetricType

def create_software_model():
    """Create the software model of the eco-vehicle system"""
    model = Model(name="EcoVehicleSystem")
    
    # Create software components
    controller = Component(
        name="VehicleController",
        stereotype="controller"
    )
    
    optimizer = Component(
        name="RouteOptimizer",
        stereotype="service"
    )
    
    monitor = Component(
        name="EmissionMonitor",
        stereotype="service"
    )
    
    sensor_hub = Component(
        name="SensorHub",
        stereotype="hardware"
    )
    
    return model, controller, optimizer, monitor, sensor_hub

def create_physical_components():
    """Create physical components of the eco-vehicle"""
    components = [
        PhysicalComponent(
            name="EngineControl",
            cad_file="engine_control.dxf",
            dimensions=(30, 20, 10),
            mass=0.5,
            material="Aluminum"
        ),
        PhysicalComponent(
            name="SensorArray",
            cad_file="sensor_array.dxf",
            dimensions=(10, 10, 5),
            mass=0.2,
            material="Plastic"
        ),
        PhysicalComponent(
            name="EmissionSensor",
            cad_file="emission_sensor.dxf",
            dimensions=(5, 5, 3),
            mass=0.1,
            material="Composite"
        )
    ]
    return components

def generate_sequence_diagram(model, components):
    """Generate an enhanced sequence diagram with timing and parallel execution"""
    generator = SequenceDiagramGenerator(model)
    
    # Add lifelines
    generator.add_lifeline("driver", "Driver", is_actor=True)
    generator.add_lifeline("controller", "VehicleController")
    generator.add_lifeline("optimizer", "RouteOptimizer")
    generator.add_lifeline("monitor", "EmissionMonitor")
    generator.add_lifeline("sensors", "SensorHub")
    
    # Add parallel sensor readings
    generator.add_message(
        source="controller",
        target="sensors",
        message="initializeSensors()",
        is_async=True,
        start_time=0.0,
        duration=1.0,
        is_parallel=True,
        parallel_group="sensor_init"
    )
    
    generator.add_message(
        source="sensors",
        target="sensors",
        message="calibrateSensors()",
        is_async=True,
        start_time=1.0,
        duration=2.0,
        is_parallel=True,
        parallel_group="sensor_init"
    )
    
    # Main sequence
    generator.add_message(
        source="driver",
        target="controller",
        message="startJourney(destination)",
        start_time=0.0
    )
    
    generator.add_message(
        source="controller",
        target="optimizer",
        message="optimizeRoute(current, destination)",
        start_time=1.0,
        duration=1.5
    )
    
    # Parallel emission monitoring
    generator.add_message(
        source="controller",
        target="monitor",
        message="startEmissionMonitoring()",
        is_parallel=True,
        parallel_group="monitoring"
    )
    
    generator.add_message(
        source="monitor",
        target="sensors",
        message="getEmissionData()",
        is_parallel=True,
        parallel_group="monitoring",
        duration=0.5
    )
    
    # Generate diagram
    generator.generate("sequence_diagram_enhanced")

def setup_model_integration(model, software_components, physical_components):
    """Set up integration between software and physical components"""
    integrator = ModelIntegrator(model, Path("outputs/cad"))
    
    # Add physical components
    for component in physical_components:
        integrator.add_physical_component(component)
    
    # Create mappings
    mappings = [
        ComponentMapping(
            software_components[0],  # VehicleController
            physical_components[0]   # EngineControl
        ),
        ComponentMapping(
            software_components[3],  # SensorHub
            physical_components[1]   # SensorArray
        ),
        ComponentMapping(
            software_components[2],  # EmissionMonitor
            physical_components[2]   # EmissionSensor
        )
    ]
    
    # Add mappings
    for mapping in mappings:
        integrator.add_mapping(mapping)
    
    # Generate integrated diagram
    integrator.generate_integrated_diagram("integrated_view.dxf")
    
    # Validate design
    warnings = integrator.validate_design()
    if warnings:
        print("\nDesign Warnings:")
        for warning in warnings:
            print(f"- {warning}")

def setup_agile_monitoring():
    """Set up agile process monitoring with enhanced metrics"""
    monitor = AgileProcessMonitor()
    
    # Start a new sprint
    monitor.start_sprint(
        sprint_id="ECO-2025-S1",
        goals=[
            "Implement enhanced sensor integration",
            "Add real-time emission monitoring",
            "Create physical-software component mapping"
        ]
    )
    
    # Record comprehensive metrics
    monitor.record_metric(
        metric_type=AgileMetricType.CUSTOMER_COLLABORATION,
        value=0.85,
        details={
            "feedback_sessions": "3",
            "implemented_suggestions": "5",
            "customer_satisfaction": "4.5/5"
        }
    )
    
    monitor.record_metric(
        metric_type=AgileMetricType.TECHNICAL_DEBT,
        value=0.75,
        details={
            "code_coverage": "85%",
            "documentation_coverage": "90%",
            "architectural_compliance": "95%",
            "test_automation": "80%"
        }
    )
    
    monitor.record_metric(
        metric_type=AgileMetricType.CROSS_FUNCTIONAL,
        value=0.90,
        details={
            "mechanical_software_alignment": "95%",
            "hardware_software_integration": "85%",
            "team_collaboration": "90%"
        }
    )
    
    return monitor

def main():
    """Main demo function"""
    print("1. Creating software model...")
    model, *software_components = create_software_model()
    
    print("\n2. Creating physical components...")
    physical_components = create_physical_components()
    
    print("\n3. Generating enhanced sequence diagram...")
    generate_sequence_diagram(model, software_components)
    print("Sequence diagram saved as 'sequence_diagram_enhanced.png'")
    
    print("\n4. Setting up model integration...")
    setup_model_integration(model, software_components, physical_components)
    print("Integrated diagram saved as 'integrated_view.dxf'")
    
    print("\n5. Setting up Agile process monitoring...")
    agile_monitor = setup_agile_monitoring()
    
    print("\nCurrent sprint health:")
    health = agile_monitor.get_sprint_health()
    for metric, value in health.items():
        print(f"- {metric}: {value:.2f}")
    
    print("\nDemo completed successfully!")
    print("Generated files:")
    print("- sequence_diagram_enhanced.png - Shows timing and parallel execution")
    print("- integrated_view.dxf - Shows software-physical component mapping")
    print("- outputs/cad/* - Contains individual CAD files for physical components")

if __name__ == "__main__":
    main()
