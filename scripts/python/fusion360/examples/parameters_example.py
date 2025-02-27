"""
Example of working with parametric design in Fusion 360
"""
import adsk.core
import adsk.fusion
import traceback
from ..fusion_client import FusionClient

def create_parametric_box():
    client = FusionClient()
    
    try:
        if not client.initialize():
            print("Failed to initialize Fusion 360")
            return
            
        # Create new design
        design = client.create_new_design("Parametric_Example")
        
        # Create user parameters
        userParams = design.userParameters
        
        # Add length, width, height parameters
        lengthParam = userParams.add("length", adsk.core.ValueInput.createByReal(10.0))
        widthParam = userParams.add("width", adsk.core.ValueInput.createByReal(5.0))
        heightParam = userParams.add("height", adsk.core.ValueInput.createByReal(3.0))
        
        # Get root component
        rootComp = design.rootComponent
        sketches = rootComp.sketches
        
        # Create sketch
        sketch = sketches.add(rootComp.xYConstructionPlane)
        lines = sketch.sketchCurves.sketchLines
        
        # Create rectangle using parameters
        startPoint = adsk.core.Point3D.create(0, 0, 0)
        endPoint = adsk.core.Point3D.create(
            lengthParam.value,
            widthParam.value,
            0
        )
        lines.addTwoPointRectangle(startPoint, endPoint)
        
        # Extrude using height parameter
        extrudes = rootComp.features.extrudeFeatures
        prof = sketch.profiles.item(0)
        distance = adsk.core.ValueInput.createByReal(heightParam.value)
        extrude = extrudes.addSimple(
            prof,
            distance,
            adsk.fusion.FeatureOperations.NewBodyFeatureOperation
        )
        
        print("Parametric box created successfully!")
        print(f"Parameters: length={lengthParam.value}, width={widthParam.value}, height={heightParam.value}")
        
        # Save the design
        client.save_design("parametric_box.f3d")
        
    except:
        if client.ui:
            client.ui.messageBox(f'Failed:\n{traceback.format_exc()}')

def modify_parameters():
    client = FusionClient()
    
    try:
        if not client.initialize():
            print("Failed to initialize Fusion 360")
            return
            
        design = client.app.activeProduct
        
        # Modify existing parameters
        params = design.userParameters
        
        # Update values
        params.itemByName("length").value = 15.0
        params.itemByName("width").value = 7.5
        params.itemByName("height").value = 4.0
        
        print("Parameters updated successfully!")
        
    except:
        if client.ui:
            client.ui.messageBox(f'Failed:\n{traceback.format_exc()}')

if __name__ == '__main__':
    create_parametric_box()
    # Uncomment to modify parameters
    # modify_parameters()
