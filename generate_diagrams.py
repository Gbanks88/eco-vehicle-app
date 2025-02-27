#!/usr/bin/env python3
"""Generate PlantUML diagrams."""

import os
from pathlib import Path
import plantuml

def generate_diagrams():
    """Generate all PlantUML diagrams in the docs/diagrams directory."""
    # Create PlantUML instance
    plantuml_instance = plantuml.PlantUML(url='http://www.plantuml.com/plantuml/img/')
    
    # Get all .puml files
    diagrams_dir = Path('docs/diagrams')
    puml_files = list(diagrams_dir.glob('*.puml'))
    
    print(f"Found {len(puml_files)} diagram files")
    
    # Generate each diagram
    for puml_file in puml_files:
        output_file = puml_file.with_suffix('.png')
        print(f"Generating {output_file}")
        
        # Read PUML content
        with open(puml_file, 'r') as f:
            puml_content = f.read()
        
        # Generate diagram
        try:
            plantuml_instance.processes_file(str(puml_file))
            print(f"Successfully generated {output_file}")
        except Exception as e:
            print(f"Error generating {output_file}: {e}")

if __name__ == '__main__':
    generate_diagrams()
