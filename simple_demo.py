"""
Simple demo of UML diagram generation
"""

from src.modeling.uml.core import Model
from src.modeling.uml.diagrams.sequence import SequenceDiagramGenerator

def main():
    """Main demo function"""
    # Create model
    model = Model(name="SimpleDemo")
    
    # Create sequence diagram
    generator = SequenceDiagramGenerator(model)
    
    # Add lifelines
    generator.add_lifeline("user", "User", is_actor=True)
    generator.add_lifeline("system", "System")
    generator.add_lifeline("database", "Database")
    
    # Add messages
    generator.add_message(
        source="user",
        target="system",
        message="request(data)"
    )
    
    generator.add_message(
        source="system",
        target="database",
        message="query()",
        is_async=True
    )
    
    generator.add_message(
        source="database",
        target="system",
        message="result",
        is_async=True
    )
    
    generator.add_message(
        source="system",
        target="user",
        message="response(data)"
    )
    
    # Generate diagram
    generator.generate("simple_sequence")
    print("Generated simple_sequence.png")

if __name__ == "__main__":
    main()
