"""
Example of creating 3D objects using extrusion in Fusion 360
"""
import adsk.core
import adsk.fusion
import traceback
from ..fusion_client import FusionClient

def create_simple_box():
    client = FusionClient()
    
    try:
        if not client.initialize():
            print("Failed to initialize Fusion 360")
            return
            
        # Create new design
        design = client.create_new_design("Extrude_Example")
        rootComp = design.rootComponent
        
        # Create sketch
        sketches = rootComp.sketches
        sketch = sketches.add(rootComp.xYConstructionPlane)
        
        # Draw a rectangle
        lines = sketch.sketchCurves.sketchLines
        startPoint = adsk.core.Point3D.create(0, 0, 0)
        endPoint = adsk.core.Point3D.create(5, 5, 0)
        lines.addTwoPointRectangle(startPoint, endPoint)
        
        # Create extrusion
        extrudes = rootComp.features.extrudeFeatures
        prof = sketch.profiles.item(0)
        
        # Extrude the rectangle by 2cm
        distance = adsk.core.ValueInput.createByReal(2.0)
        extrude = extrudes.addSimple(
            prof,                                  # Profile to extrude
            distance,                              # Distance to extrude
            adsk.fusion.FeatureOperations.NewBodyFeatureOperation  # Operation type
        )
        
        print("Box created successfully!")
        
        # Save the design
        client.save_design("simple_box.f3d")
        
        # Export as STL
        client.export_design("simple_box.stl", "stl")
        
    except:
        if client.ui:
            client.ui.messageBox(f'Failed:\n{traceback.format_exc()}')

if __name__ == '__main__':
    create_simple_box()
