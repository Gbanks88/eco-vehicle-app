"""
Example of creating patterns in Fusion 360
"""
import adsk.core
import adsk.fusion
import traceback
from ..fusion_client import FusionClient

def create_circular_pattern():
    client = FusionClient()
    
    try:
        if not client.initialize():
            print("Failed to initialize Fusion 360")
            return
            
        # Create new design
        design = client.create_new_design("Pattern_Example")
        rootComp = design.rootComponent
        
        # Create base cylinder
        sketches = rootComp.sketches
        sketch = sketches.add(rootComp.xYConstructionPlane)
        circles = sketch.sketchCurves.sketchCircles
        circle = circles.addByCenterRadius(
            adsk.core.Point3D.create(0, 0, 0),
            0.5  # radius
        )
        
        # Extrude the circle
        extrudes = rootComp.features.extrudeFeatures
        prof = sketch.profiles.item(0)
        distance = adsk.core.ValueInput.createByReal(1.0)
        baseFeature = extrudes.addSimple(
            prof,
            distance,
            adsk.fusion.FeatureOperations.NewBodyFeatureOperation
        )
        
        # Create circular pattern
        circularFeats = rootComp.features.circularPatternFeatures
        inputEntities = adsk.core.ObjectCollection.create()
        inputEntities.add(baseFeature)
        
        # Pattern parameters
        axisPoint = adsk.core.Point3D.create(0, 0, 0)
        axisVector = adsk.core.Vector3D.create(0, 0, 1)
        axis = rootComp.constructionAxes.addByCurveAndStartPoint(
            rootComp.xConstructionAxis,
            axisPoint
        )
        
        circularFeats.addByAngleAndCount(
            inputEntities,          # Features to pattern
            axis,                   # Axis to pattern around
            adsk.core.ValueInput.createByReal(2 * 3.14159),  # Total angle
            6,                      # Number of instances
            True,                   # Symmetric pattern
            adsk.core.ValueInput.createByString("0 cm")  # Offset
        )
        
        print("Circular pattern created successfully!")
        
        # Save the design
        client.save_design("circular_pattern.f3d")
        
    except:
        if client.ui:
            client.ui.messageBox(f'Failed:\n{traceback.format_exc()}')

def create_rectangular_pattern():
    client = FusionClient()
    
    try:
        if not client.initialize():
            print("Failed to initialize Fusion 360")
            return
            
        # Create new design
        design = client.create_new_design("Rectangular_Pattern")
        rootComp = design.rootComponent
        
        # Create base cube
        sketches = rootComp.sketches
        sketch = sketches.add(rootComp.xYConstructionPlane)
        lines = sketch.sketchCurves.sketchLines
        square = lines.addTwoPointRectangle(
            adsk.core.Point3D.create(0, 0, 0),
            adsk.core.Point3D.create(1, 1, 0)
        )
        
        # Extrude the square
        extrudes = rootComp.features.extrudeFeatures
        prof = sketch.profiles.item(0)
        distance = adsk.core.ValueInput.createByReal(1.0)
        baseFeature = extrudes.addSimple(
            prof,
            distance,
            adsk.fusion.FeatureOperations.NewBodyFeatureOperation
        )
        
        # Create rectangular pattern
        rectFeats = rootComp.features.rectangularPatternFeatures
        inputEntities = adsk.core.ObjectCollection.create()
        inputEntities.add(baseFeature)
        
        # Pattern parameters
        xDir = rootComp.xConstructionAxis.geometry.direction
        yDir = rootComp.yConstructionAxis.geometry.direction
        
        rectFeats.addBySpacingAndCount(
            inputEntities,          # Features to pattern
            xDir,                   # X direction
            adsk.core.ValueInput.createByReal(2.0),  # X spacing
            3,                      # X count
            yDir,                   # Y direction
            adsk.core.ValueInput.createByReal(2.0),  # Y spacing
            3,                      # Y count
            True,                   # Symmetric pattern
            adsk.core.ValueInput.createByString("0 cm")  # Offset
        )
        
        print("Rectangular pattern created successfully!")
        
        # Save the design
        client.save_design("rectangular_pattern.f3d")
        
    except:
        if client.ui:
            client.ui.messageBox(f'Failed:\n{traceback.format_exc()}')

if __name__ == '__main__':
    create_circular_pattern()
    create_rectangular_pattern()
