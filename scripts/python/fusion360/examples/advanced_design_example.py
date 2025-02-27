"""
Advanced design example showcasing sophisticated modeling techniques in Fusion 360
"""
import adsk.core
import adsk.fusion
import traceback
import math
from ..fusion_client import FusionClient

def create_advanced_design():
    client = FusionClient()
    
    try:
        if not client.initialize():
            print("Failed to initialize Fusion 360")
            return
            
        # Create new design
        design = client.create_new_design("Advanced_Design_Example")
        rootComp = design.rootComponent
        
        # Create construction planes for better organization
        planes = rootComp.constructionPlanes
        planeInput = planes.createInput()
        
        # Offset plane for top features
        offsetValue = adsk.core.ValueInput.createByReal(2.0)
        planeInput.setByOffset(rootComp.xYConstructionPlane, offsetValue)
        topPlane = planes.add(planeInput)
        
        # Create base sketch
        sketches = rootComp.sketches
        baseSketch = sketches.add(rootComp.xYConstructionPlane)
        
        # Add parametric profile
        circles = baseSketch.sketchCurves.sketchCircles
        baseCircle = circles.addByCenterRadius(
            adsk.core.Point3D.create(0, 0, 0),
            3.0
        )
        
        # Add profile features
        points = []
        for i in range(6):
            angle = 2 * math.pi * i / 6
            x = 2.5 * math.cos(angle)
            y = 2.5 * math.sin(angle)
            points.append(adsk.core.Point3D.create(x, y, 0))
        
        lines = baseSketch.sketchCurves.sketchLines
        for i in range(len(points)):
            lines.addByTwoPoints(points[i], points[(i + 1) % len(points)])
        
        # Create parameters for dynamic updates
        params = design.userParameters
        height_param = params.add("height", 
            adsk.core.ValueInput.createByReal(5.0))
        pattern_param = params.add("pattern_count", 
            adsk.core.ValueInput.createByReal(6.0))
        
        # Extrude base
        extrudes = rootComp.features.extrudeFeatures
        prof = baseSketch.profiles.item(0)
        extInput = extrudes.createInput(prof, adsk.fusion.FeatureOperations.NewBodyFeatureOperation)
        extInput.setDistanceExtent(False, 
            adsk.core.ValueInput.createByString("height"))
        baseExtrude = extrudes.add(extInput)
        
        # Create pattern on top face
        topSketch = sketches.add(topPlane)
        
        # Add pattern circles
        patternCircles = []
        radius = 0.3
        for i in range(6):
            angle = 2 * math.pi * i / 6
            x = 2.0 * math.cos(angle)
            y = 2.0 * math.sin(angle)
            patternCircles.append(
                topSketch.sketchCurves.sketchCircles.addByCenterRadius(
                    adsk.core.Point3D.create(x, y, 0),
                    radius
                )
            )
            
        # Extrude pattern features
        for circle in patternCircles:
            prof = topSketch.profiles.item(topSketch.profiles.count - 1)
            extInput = extrudes.createInput(prof, adsk.fusion.FeatureOperations.CutFeatureOperation)
            extInput.setDistanceExtent(False, 
                adsk.core.ValueInput.createByReal(1.0))
            extrudes.add(extInput)
            
        # Add fillets
        fillets = rootComp.features.filletFeatures
        edges = adsk.core.ObjectCollection.create()
        
        # Collect bottom edges
        body = rootComp.bRepBodies.item(0)
        for edge in body.edges:
            if abs(edge.startVertex.geometry.z) < 0.001:
                edges.add(edge)
                
        filletInput = fillets.createInput()
        filletInput.addConstantRadiusEdgeSet(edges, 
            adsk.core.ValueInput.createByReal(0.2))
        fillets.add(filletInput)
        
        # Add shell for hollow body
        shells = rootComp.features.shellFeatures
        shellInput = shells.createInput([body])
        shellInput.insideThickness = adsk.core.ValueInput.createByReal(0.1)
        shells.add(shellInput)
        
        # Add thread feature
        threads = rootComp.features.threadFeatures
        threadData = threads.threadTypes.item(0)
        
        # Find cylindrical face for thread
        threadFace = None
        for face in body.faces:
            if face.geometry.surfaceType == adsk.core.SurfaceTypes.CylinderSurfaceType:
                if abs(face.boundingBox.maxPoint.z - 5.0) < 0.001:
                    threadFace = face
                    break
                    
        if threadFace:
            threadInput = threads.createInput(threadFace, threadData)
            threads.add(threadInput)
        
        # Save design
        client.save_design("advanced_parametric_design.f3d")
        
        print("Advanced design created successfully!")
        print(f"Parameters: height={height_param.value}, pattern_count={pattern_param.value}")
        
    except:
        if client.ui:
            client.ui.messageBox(f'Failed:\n{traceback.format_exc()}')

if __name__ == '__main__':
    create_advanced_design()
