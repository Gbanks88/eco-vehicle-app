"""
Example of creating and manipulating sketches in Fusion 360
"""
import adsk.core
import adsk.fusion
import traceback
from ..fusion_client import FusionClient

def create_rectangle_sketch():
    client = FusionClient()
    
    try:
        if not client.initialize():
            print("Failed to initialize Fusion 360")
            return
            
        # Get the new design
        design = client.create_new_design("Sketch_Example")
        
        # Get the root component
        rootComp = design.rootComponent
        
        # Create a new sketch on the xy plane
        sketches = rootComp.sketches
        xyPlane = rootComp.xYConstructionPlane
        sketch = sketches.add(xyPlane)
        
        # Create a rectangle
        lines = sketch.sketchCurves.sketchLines
        startPoint = adsk.core.Point3D.create(0, 0, 0)
        endPoint = adsk.core.Point3D.create(5, 5, 0)
        lines.addTwoPointRectangle(startPoint, endPoint)
        
        print("Rectangle sketch created successfully!")
        
        # Save the design
        client.save_design("rectangle_sketch.f3d")
        
    except:
        if client.ui:
            client.ui.messageBox(f'Failed:\n{traceback.format_exc()}')

if __name__ == '__main__':
    create_rectangle_sketch()
