"""
Demo script showing UML diagram generation and Agile process monitoring.
"""

from datetime import datetime
from src.modeling.uml.core import Model, Class, Operation
from src.modeling.uml.diagrams.sequence import SequenceDiagramGenerator
from src.modeling.uml.diagrams.component import ComponentDiagramGenerator
from src.modeling.uml.diagrams.deployment import DeploymentDiagramGenerator
from src.modeling.agile.process_monitor import AgileProcessMonitor, AgileMetricType

def create_eco_vehicle_model():
    """Create a sample eco-vehicle system model"""
    model = Model(name="EcoVehicleSystem")
    
    # Create classes
    vehicle_controller = Class(
        name="VehicleController",
        operations=[
            Operation(
                name="optimizeRoute",
                parameters=[("startLocation", "Location"),
                             ("endLocation", "Location")],
                return_type="Route"
            ),
            Operation(
                name="monitorEmissions",
                parameters=[],
                return_type="EmissionData"
            )
        ]
    )
    
    route_optimizer = Class(
        name="RouteOptimizer",
        operations=[
            Operation(
                name="calculateEfficientRoute",
                parameters=[("route", "Route"),
                             ("vehicleType", "VehicleType")],
                return_type="OptimizedRoute"
            )
        ]
    )
    
    emission_monitor = Class(
        name="EmissionMonitor",
        operations=[
            Operation(
                name="trackEmissions",
                parameters=[("vehicleId", "string")],
                return_type="EmissionData"
            )
        ]
    )
    
    return model, vehicle_controller, route_optimizer, emission_monitor

def generate_sequence_diagram(model, controller, optimizer, monitor):
    """Generate sequence diagram for route optimization"""
    generator = SequenceDiagramGenerator(model)
    
    # Add lifelines
    generator.add_lifeline("driver", "Driver", is_actor=True)
    generator.add_lifeline("controller", "VehicleController")
    generator.add_lifeline("optimizer", "RouteOptimizer")
    generator.add_lifeline("monitor", "EmissionMonitor")
    
    # Add messages
    generator.add_message(
        source="driver",
        target="controller",
        message="optimizeRoute(start, end)"
    )
    generator.add_message(
        source="controller",
        target="optimizer",
        message="calculateEfficientRoute(route, vehicle)"
    )
    generator.add_message(
        source="optimizer",
        target="monitor",
        message="trackEmissions(vehicleId)"
    )
    generator.add_message(
        source="monitor",
        target="optimizer",
        message="return emissionData"
    )
    generator.add_message(
        source="optimizer",
        target="controller",
        message="return optimizedRoute"
    )
    generator.add_message(
        source="controller",
        target="driver",
        message="return route"
    )
    
    # Generate and save diagram
    diagram = generator.generate()
    diagram.render("eco_vehicle_sequence", format="png", cleanup=True)
    return diagram

def generate_component_diagram(model):
    """Generate component diagram for the system"""
    generator = ComponentDiagramGenerator(model)
    
    # Add components
    ui = Component(name="UI", stereotype="boundary")
    controller = Component(name="VehicleController", stereotype="controller")
    optimizer = Component(name="RouteOptimizer", stereotype="service")
    monitor = Component(name="EmissionMonitor", stereotype="service")
    db = Component(name="Database", stereotype="database")
    
    # Add components to diagram
    ui_id = generator.add_component(ui)
    ctrl_id = generator.add_component(controller)
    opt_id = generator.add_component(optimizer)
    mon_id = generator.add_component(monitor)
    db_id = generator.add_component(db)
    
    # Add relationships
    generator.add_relation(ComponentRelation(ui_id, ctrl_id, "dependency"))
    generator.add_relation(ComponentRelation(ctrl_id, opt_id, "dependency"))
    generator.add_relation(ComponentRelation(ctrl_id, mon_id, "dependency"))
    generator.add_relation(ComponentRelation(opt_id, db_id, "dependency"))
    generator.add_relation(ComponentRelation(mon_id, db_id, "dependency"))
    
    # Generate and save diagram
    diagram = generator.generate()
    diagram.render("eco_vehicle_component", format="png", cleanup=True)
    return diagram

def setup_agile_monitor():
    """Set up agile process monitoring"""
    monitor = AgileProcessMonitor()
    
    # Start a new sprint
    monitor.start_sprint(
        sprint_id="ECO-2025-S1",
        goals=[
            "Implement route optimization algorithm",
            "Add real-time emission monitoring",
            "Create driver feedback system"
        ]
    )
    
    # Record some metrics
    monitor.record_metric(
        metric_type=AgileMetricType.CUSTOMER_COLLABORATION,
        value=0.85,
        details={
            "feedback_sessions": "3",
            "implemented_suggestions": "5"
        }
    )
    
    monitor.record_metric(
        metric_type=AgileMetricType.TECHNICAL_DEBT,
        value=0.75,
        details={
            "code_coverage": "85%",
            "documentation_coverage": "90%"
        }
    )
    
    return monitor

def main():
    """Main demo function"""
    print("Creating eco-vehicle system model...")
    model, controller, optimizer, monitor = create_eco_vehicle_model()
    
    print("\nGenerating sequence diagram...")
    sequence_diagram = generate_sequence_diagram(model, controller, optimizer, monitor)
    print("Sequence diagram saved as 'eco_vehicle_sequence.png'")
    
    print("\nGenerating component diagram...")
    component_diagram = generate_component_diagram(model)
    print("Component diagram saved as 'eco_vehicle_component.png'")
    
    print("\nSetting up Agile process monitor...")
    agile_monitor = setup_agile_monitor()
    
    print("\nCurrent sprint health:")
    health = agile_monitor.get_sprint_health()
    for metric, value in health.items():
        print(f"- {metric}: {value:.2f}")
    
    print("\nDemo completed successfully!")

if __name__ == "__main__":
    main()
