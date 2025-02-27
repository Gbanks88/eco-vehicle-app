# Eco Vehicle Modeling System

This system provides tools for modeling and analyzing eco-vehicle components, materials, and overall vehicle design.

## Setup

1. Install dependencies:
```bash
pip install -r requirements-modeling.txt
```

2. Verify installation:
```bash
python scripts/python/modeling/demo_vehicle_model.py
```

## System Components

### 1. Vehicle Model (`src/modeling/vehicle_model.py`)
- Main class for vehicle modeling and analysis
- Handles components, materials, and physical properties
- Provides stress analysis and safety factor calculations
- Includes 3D visualization capabilities

### 2. Configuration (`config/vehicle_config.json`)
- Defines materials and their properties
- Specifies component dimensions and characteristics
- Sets safety factors and stress limits
- Configures vehicle specifications

### 3. Demo Script (`scripts/python/modeling/demo_vehicle_model.py`)
- Demonstrates system usage
- Creates example vehicle model
- Performs analysis and visualization
- Exports results

## Usage Examples

### 1. Create a Vehicle Model
```python
from src.modeling.vehicle_model import VehicleModel, MaterialProperties, ComponentSpecs

# Create model
model = VehicleModel()

# Define material
aluminum = MaterialProperties(
    name="Aluminum 6061-T6",
    density=2700,
    yield_strength=276,
    thermal_conductivity=167,
    cost_per_kg=2.5
)

# Create component
chassis = ComponentSpecs(
    name="Main Chassis",
    material=aluminum,
    mass=250,
    dimensions=(4.5, 1.8, 0.15),
    max_stress=200
)

# Add to model
model.add_component(chassis)
```

### 2. Analyze Components
```python
# Calculate stress
load = 10000  # 10 kN
stress = model.calculate_stress("Main Chassis", load)

# Check safety factor
is_safe = model.check_safety_factor("Main Chassis", load)
```

### 3. Visualize Model
```python
# Visualize specific component
model.visualize_component("Main Chassis")

# Export model data
model.export_model("vehicle_model.json")
```

## File Structure
```
eco_vehicle_project/
├── src/
│   └── modeling/
│       └── vehicle_model.py
├── scripts/
│   └── python/
│       └── modeling/
│           └── demo_vehicle_model.py
├── config/
│   └── vehicle_config.json
└── requirements-modeling.txt
```

## Key Features

1. Component Management
   - Add/remove components
   - Update properties
   - Calculate mass properties

2. Material Analysis
   - Stress calculations
   - Safety factor verification
   - Thermal properties

3. Visualization
   - 3D component visualization
   - Interactive viewing
   - Export capabilities

4. Data Management
   - JSON configuration
   - Model export
   - Results logging

## Best Practices

1. Always verify material properties before use
2. Include appropriate safety factors
3. Document any modifications to components
4. Validate stress calculations
5. Back up model data regularly

## Troubleshooting

1. Installation Issues
   - Verify Python version (3.8+ required)
   - Check pip installation
   - Validate dependencies

2. Visualization Problems
   - Update matplotlib
   - Check 3D backend support
   - Verify display configuration

3. Analysis Errors
   - Validate input units
   - Check material properties
   - Verify component dimensions
