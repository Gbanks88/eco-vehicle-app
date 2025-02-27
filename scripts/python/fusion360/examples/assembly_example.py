"""
Example of creating assemblies in Fusion 360
"""
import adsk.core
import adsk.fusion
import traceback
from ..fusion_client import FusionClient

def create_simple_assembly():
    client = FusionClient()
    
    try:
        if not client.initialize():
            print("Failed to initialize Fusion 360")
            return
            
        # Create new design
        design = client.create_new_design("Assembly_Example")
        rootComp = design.rootComponent
        
        # Create the base component (box)
        base_comp = rootComp.occurrences.addNewComponent(adsk.core.Matrix3D.create())
        sketches = base_comp.component.sketches
        
        # Create base sketch
        sketch = sketches.add(base_comp.component.xYConstructionPlane)
        lines = sketch.sketchCurves.sketchLines
        base_rect = lines.addTwoPointRectangle(
            adsk.core.Point3D.create(0, 0, 0),
            adsk.core.Point3D.create(10, 10, 0)
        )
        
        # Extrude base
        extrudes = base_comp.component.features.extrudeFeatures
        prof = sketch.profiles.item(0)
        base_extrude = extrudes.addSimple(
            prof,
            adsk.core.ValueInput.createByReal(2.0),
            adsk.fusion.FeatureOperations.NewBodyFeatureOperation
        )
        
        # Create the top component (lid)
        top_comp = rootComp.occurrences.addNewComponent(adsk.core.Matrix3D.create())
        sketches = top_comp.component.sketches
        
        # Create lid sketch
        sketch = sketches.add(top_comp.component.xYConstructionPlane)
        lines = sketch.sketchCurves.sketchLines
        top_rect = lines.addTwoPointRectangle(
            adsk.core.Point3D.create(0, 0, 0),
            adsk.core.Point3D.create(10.5, 10.5, 0)
        )
        
        # Extrude lid
        extrudes = top_comp.component.features.extrudeFeatures
        prof = sketch.profiles.item(0)
        top_extrude = extrudes.addSimple(
            prof,
            adsk.core.ValueInput.createByReal(1.0),
            adsk.fusion.FeatureOperations.NewBodyFeatureOperation
        )
        
        # Move the lid component
        transform = adsk.core.Matrix3D.create()
        transform.translation = adsk.core.Vector3D.create(0, 0, 2.0)
        top_comp.transform = transform
        
        # Add joints
        joints = rootComp.joints
        
        # Create a rigid joint between base and lid
        geo0 = base_comp.component.faces.item(0)  # Top face of base
        geo1 = top_comp.component.faces.item(0)   # Bottom face of lid
        
        jointGeometry = joints.createGeometry(geo0)
        jointInput = joints.createInput(jointGeometry)
        jointInput.setAsRigidJointMotion()
        joint = joints.add(jointInput)
        
        print("Assembly created successfully!")
        
        # Save the design
        client.save_design("simple_assembly.f3d")
        
    except:
        if client.ui:
            client.ui.messageBox(f'Failed:\n{traceback.format_exc()}')

if __name__ == '__main__':
    create_simple_assembly()
