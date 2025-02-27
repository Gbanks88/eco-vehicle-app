"""
Enhanced example of working with advanced constraints and measurements in Fusion 360
"""
import adsk.core
import adsk.fusion
import traceback
import math
from ..fusion_client import FusionClient

def create_advanced_constrained_sketch():
    client = FusionClient()
    
    try:
        if not client.initialize():
            print("Failed to initialize Fusion 360")
            return
            
        # Create new design
        design = client.create_new_design("Advanced_Constraints_Example")
        rootComp = design.rootComponent
        
        # Create sketch
        sketches = rootComp.sketches
        sketch = sketches.add(rootComp.xYConstructionPlane)
        
        # Get sketch curves
        lines = sketch.sketchCurves.sketchLines
        circles = sketch.sketchCurves.sketchCircles
        arcs = sketch.sketchCurves.sketchArcs
        
        # Create base hexagon
        points = []
        radius = 3.0
        for i in range(6):
            angle = 2 * math.pi * i / 6
            x = radius * math.cos(angle)
            y = radius * math.sin(angle)
            points.append(adsk.core.Point3D.create(x, y, 0))
            
        hexLines = []
        for i in range(len(points)):
            hexLines.append(lines.addByTwoPoints(
                points[i], 
                points[(i + 1) % len(points)]
            ))
        
        # Create inner pattern
        innerCircle = circles.addByCenterRadius(
            adsk.core.Point3D.create(0, 0, 0),
            1.5
        )
        
        # Add arcs connecting to inner circle
        connectingArcs = []
        for i in range(0, len(points), 2):
            midPoint = adsk.core.Point3D.create(
                points[i].x * 0.6,
                points[i].y * 0.6,
                0
            )
            connectingArcs.append(arcs.addByThreePoints(
                points[i],
                midPoint,
                adsk.core.Point3D.create(
                    points[i].x * 0.5,
                    points[i].y * 0.5,
                    0
                )
            ))
        
        # Add dimensional constraints
        dims = sketch.sketchDimensions
        
        # Constrain hexagon size
        radius_dim = dims.addRadialDimension(
            innerCircle,
            adsk.core.Point3D.create(2, 2, 0)
        )
        
        # Add geometric constraints
        constraints = sketch.geometricConstraints
        
        # Make hexagon regular
        for i in range(len(hexLines)):
            constraints.addEqual(
                hexLines[i],
                hexLines[(i + 1) % len(hexLines)]
            )
            
        # Center inner circle
        constraints.addConcentric(
            innerCircle,
            adsk.core.Point3D.create(0, 0, 0)
        )
        
        # Make connecting arcs symmetric
        for i in range(len(connectingArcs)):
            if i > 0:
                constraints.addSymmetry(
                    connectingArcs[i],
                    connectingArcs[0],
                    hexLines[0]
                )
        
        # Add parameters for dynamic updates
        params = design.userParameters
        
        # Create parameters
        outer_radius = params.add(
            "outer_radius",
            adsk.core.ValueInput.createByReal(radius)
        )
        inner_radius = params.add(
            "inner_radius",
            adsk.core.ValueInput.createByReal(radius_dim.parameter.value)
        )
        
        # Link dimensions to parameters
        radius_dim.parameter.expression = "inner_radius"
        
        # Add construction lines for reference
        centerPoint = sketch.sketchPoints.add(
            adsk.core.Point3D.create(0, 0, 0)
        )
        for point in points:
            refLine = lines.addByTwoPoints(
                centerPoint,
                point
            )
            refLine.isConstruction = True
            
        print("Advanced constrained sketch created successfully!")
        print(f"Parameters: outer_radius={outer_radius.value}, inner_radius={inner_radius.value}")
        
        # Save the design
        client.save_design("advanced_constrained_sketch.f3d")
        
    except:
        if client.ui:
            client.ui.messageBox(f'Failed:\n{traceback.format_exc()}')

def add_advanced_measurements():
    client = FusionClient()
    
    try:
        if not client.initialize():
            print("Failed to initialize Fusion 360")
            return
            
        design = client.app.activeProduct
        rootComp = design.rootComponent
        
        # Get the first sketch
        sketch = rootComp.sketches.item(0)
        
        # Add measurements
        measurements = sketch.sketchDimensions
        
        # Measure distances between features
        circle = sketch.sketchCurves.sketchCircles.item(0)
        arc = sketch.sketchCurves.sketchArcs.item(0)
        
        # Add angle measurement
        angle_measurement = measurements.addAngularDimension(
            arc,
            sketch.sketchCurves.sketchLines.item(0),
            adsk.core.Point3D.create(2, 1, 0)
        )
        
        # Add radial measurements
        radial_measurement = measurements.addRadialDimension(
            circle,
            adsk.core.Point3D.create(-2, 2, 0)
        )
        
        print("Measurements added:")
        print(f"Arc angle: {angle_measurement.parameter.value} degrees")
        print(f"Inner circle radius: {radial_measurement.parameter.value} cm")
        
    except:
        if client.ui:
            client.ui.messageBox(f'Failed:\n{traceback.format_exc()}')

if __name__ == '__main__':
    create_advanced_constrained_sketch()
    # Uncomment to add measurements
    # add_advanced_measurements()
