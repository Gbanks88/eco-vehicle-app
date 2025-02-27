"""
Example usage of the UML modeling system
"""
from src.modeling.uml.core import (
    Model, Package, Class, Attribute, Operation,
    Association, Generalization
)
from src.modeling.uml.diagrams import DiagramGenerator
from src.modeling.uml.serialization import ModelSerializer

def create_example_model() -> Model:
    """Create an example UML model"""
    # Create model
    model = Model("Example System")

    # Create main package
    main_package = Package("com.example")

    # Create classes
    vehicle_class = Class(
        name="Vehicle",
        is_abstract=True
    )
    vehicle_class.add_attribute(Attribute("id", "String", "private"))
    vehicle_class.add_attribute(Attribute("model", "String", "protected"))
    vehicle_class.add_operation(Operation(
        "start",
        "void",
        visibility="public",
        is_abstract=True
    ))

    car_class = Class(name="Car")
    car_class.add_attribute(Attribute("engine", "Engine", "private"))
    car_class.add_operation(Operation(
        "start",
        "void",
        visibility="public"
    ))

    engine_class = Class(name="Engine")
    engine_class.add_attribute(Attribute("power", "int", "private"))
    engine_class.add_operation(Operation(
        "getPower",
        "int",
        visibility="public"
    ))

    # Add classes to package
    main_package.add_element(vehicle_class)
    main_package.add_element(car_class)
    main_package.add_element(engine_class)

    # Add package to model
    model.add_package(main_package)

    # Create relationships
    inheritance = Generalization(
        name="Car_Vehicle_Inheritance",
        source=car_class.id,
        target=vehicle_class.id,
        relationship_type="generalization"
    )

    association = Association(
        name="Car_Engine_Association",
        source=car_class.id,
        target=engine_class.id,
        relationship_type="association",
        multiplicity_source="1",
        multiplicity_target="1"
    )

    # Add relationships to model
    model.add_relationship(inheritance)
    model.add_relationship(association)

    return model

def main():
    """Main example function"""
    # Create model
    model = create_example_model()

    # Generate class diagram
    generator = DiagramGenerator(model)
    diagram = generator.generate_class_diagram()
    
    # Save diagram
    diagram.render("example_class_diagram", format="png", cleanup=True)

    # Serialize model
    serializer = ModelSerializer()
    
    # Save as JSON
    with open("example_model.json", "w") as f:
        f.write(serializer.to_json(model))

    # Save as YAML
    with open("example_model.yaml", "w") as f:
        f.write(serializer.to_yaml(model))

    print("Example model and diagrams have been generated!")

if __name__ == "__main__":
    main()
