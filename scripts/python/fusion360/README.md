# Fusion 360 Integration Example

This directory contains examples and utilities for working with the Fusion 360 API.

## Setup

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Configure environment variables in `.env`:
```env
FUSION_API_VERSION="v1"
FUSION_BASE_URL="https://developer.api.autodesk.com/fusion360"
```

3. Make sure Fusion 360 is installed and running

## Running the Example

1. Open Fusion 360
2. Run the example script:
```bash
python example.py
```

The example will:
- Create a new design
- Save it in Fusion 360 format
- Export it to STL and STEP formats

## Example Scripts

The `examples` directory contains several scripts demonstrating different Fusion 360 features:

1. `sketch_example.py`: Creating 2D sketches
   - Creates a simple rectangle sketch
   - Shows basic sketch manipulation
   - Demonstrates working with construction planes

2. `extrude_example.py`: 3D modeling with extrusion
   - Creates a basic 3D box
   - Shows how to extrude 2D profiles
   - Includes STL export

3. `parameters_example.py`: Parametric design
   - Creates a parametric box
   - Shows how to create and modify parameters
   - Demonstrates dynamic model updates

4. `pattern_example.py`: Creating patterns
   - Circular pattern of cylinders
   - Rectangular pattern of cubes
   - Pattern parameters and spacing

5. `assembly_example.py`: Working with assemblies
   - Creating multiple components
   - Component positioning
   - Joint creation
   - Assembly constraints

6. `constraints_example.py`: Geometric constraints
   - Dimensional constraints
   - Geometric relationships
   - Parametric measurements
   - Design parameters

7. `advanced_design_example.py`: Complex parametric design
   - Construction planes and advanced organization
   - Parametric base profiles
   - Pattern features and arrays
   - Advanced feature operations (fillets, shells, threads)
   - Dynamic parameter updates
   - Complex body modifications

To run any example:
```bash
# Make sure Fusion 360 is running first
python examples/sketch_example.py
python examples/extrude_example.py
python examples/parameters_example.py
python examples/pattern_example.py
python examples/assembly_example.py
python examples/constraints_example.py
python examples/advanced_design_example.py
```

## Common Operations

1. Creating a Sketch:
```python
design = client.create_new_design("Example")
rootComp = design.rootComponent
sketch = rootComp.sketches.add(rootComp.xYConstructionPlane)
```

2. Basic Extrusion:
```python
distance = adsk.core.ValueInput.createByReal(2.0)
extrude = extrudes.addSimple(profile, distance, 
    adsk.fusion.FeatureOperations.NewBodyFeatureOperation)
```

3. Working with Parameters:
```python
userParams = design.userParameters
lengthParam = userParams.add("length", 
    adsk.core.ValueInput.createByReal(10.0))
```

## Advanced Operations

1. Creating Patterns:
```python
# Circular pattern
circularFeats.addByAngleAndCount(
    inputEntities,    # Features to pattern
    axis,            # Axis to pattern around
    angle,           # Total angle
    count,           # Number of instances
    isSymmetric      # Symmetric pattern
)

# Rectangular pattern
rectFeats.addBySpacingAndCount(
    inputEntities,    # Features to pattern
    xDir,            # X direction
    xSpacing,        # X spacing
    xCount,          # X count
    yDir,            # Y direction
    ySpacing,        # Y spacing
    yCount           # Y count
)
```

2. Working with Assemblies:
```python
# Create new component
newComp = rootComp.occurrences.addNewComponent(
    adsk.core.Matrix3D.create()
)

# Add joint
joints = rootComp.joints
jointGeometry = joints.createGeometry(geo0)
jointInput = joints.createInput(jointGeometry)
joint = joints.add(jointInput)
```

3. Adding Constraints:
```python
# Dimensional constraint
dims.addDistanceDimension(
    point1,
    point2,
    orientation,
    textPosition
)

# Geometric constraint
constraints.addPerpendicular(line1, line2)
constraints.addMidPoint(point, line)
```

## Advanced Design Features

1. Construction and Organization:
```python
# Create offset construction plane
planeInput = planes.createInput()
planeInput.setByOffset(
    rootComp.xYConstructionPlane,
    offsetValue
)
topPlane = planes.add(planeInput)
```

2. Advanced Features:
```python
# Add fillet feature
filletInput = fillets.createInput()
filletInput.addConstantRadiusEdgeSet(
    edges,
    radius
)
fillets.add(filletInput)

# Create shell feature
shellInput = shells.createInput([body])
shellInput.insideThickness = thickness
shells.add(shellInput)

# Add thread feature
threadInput = threads.createInput(face, threadData)
threads.add(threadInput)
```

3. Parametric Relationships:
```python
# Create dynamic parameters
params = design.userParameters
height_param = params.add(
    "height",
    adsk.core.ValueInput.createByReal(5.0)
)

# Link features to parameters
extInput.setDistanceExtent(
    False,
    adsk.core.ValueInput.createByString("height")
)
```

4. Advanced Constraints:
```python
# Add geometric symmetry
constraints.addSymmetry(
    entity1,
    entity2,
    symmetryLine
)

# Create concentric constraint
constraints.addConcentric(
    circle,
    centerPoint
)

# Add equal length constraint
constraints.addEqual(
    line1,
    line2
)
```

## File Structure

- `fusion_client.py`: Main integration class
- `config.py`: Configuration settings
- `example.py`: Usage examples
- `.env`: Environment variables (create this file)

## Common Issues

1. If Fusion 360 is not running, the example will fail to initialize
2. Make sure you have proper permissions in the save directory
3. Check that all environment variables are set correctly

## Additional Resources

- [Fusion 360 API Documentation](https://help.autodesk.com/cloudhelp/ENU/Fusion-360-API/files/index.html)
- [API Reference](https://help.autodesk.com/cloudhelp/ENU/Fusion-360-API/files/ReferenceManual_UM.htm)
