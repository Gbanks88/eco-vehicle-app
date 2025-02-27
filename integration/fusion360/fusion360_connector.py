import adsk.core
import adsk.fusion
import adsk.cam
import traceback
import json
import os
from typing import Dict, List, Optional

class Fusion360Connector:
    def __init__(self):
        self.app = adsk.core.Application.get()
        self.ui = self.app.userInterface
        self.design = self.app.activeProduct
        self.root_comp = self.design.rootComponent
        self.config_path = os.path.join(os.path.dirname(__file__), '../../config/vehicle_config.json')

    def load_vehicle_config(self) -> Dict:
        """Load vehicle configuration from JSON"""
        with open(self.config_path, 'r') as f:
            return json.load(f)

    def create_eco_vehicle_model(self, config: Dict):
        """Create the eco vehicle model in Fusion 360"""
        try:
            # Create main body
            body_dims = config['body_dimensions']
            body = self.create_body_component(
                length=body_dims['length'],
                width=body_dims['width'],
                height=body_dims['height']
            )

            # Add wheels
            wheel_config = config['wheels']
            self.add_wheels(
                wheel_diameter=wheel_config['diameter'],
                wheel_width=wheel_config['width'],
                wheel_positions=wheel_config['positions']
            )

            # Add solar panels
            if config.get('solar_panels'):
                self.add_solar_panels(config['solar_panels'])

            # Add battery compartment
            if config.get('battery'):
                self.add_battery_compartment(config['battery'])

        except:
            if self.ui:
                self.ui.messageBox('Failed:\n{}'.format(traceback.format_exc()))

    def create_body_component(self, length: float, width: float, height: float) -> adsk.fusion.Component:
        """Create the main body component"""
        sketches = self.root_comp.sketches
        xy_plane = self.root_comp.xYConstructionPlane
        sketch = sketches.add(xy_plane)
        
        # Create body profile
        lines = sketch.sketchCurves.sketchLines
        start_point = adsk.core.Point3D.create(0, 0, 0)
        lines.addTwoPointRectangle(
            start_point,
            adsk.core.Point3D.create(length, width, 0)
        )
        
        # Extrude to create 3D body
        profile = sketch.profiles.item(0)
        extrudes = self.root_comp.features.extrudeFeatures
        ext_input = extrudes.createInput(
            profile,
            adsk.fusion.FeatureOperations.NewBodyFeatureOperation
        )
        ext_input.setDistanceExtent(
            False,
            adsk.core.ValueInput.createByReal(height)
        )
        return extrudes.add(ext_input)

    def add_wheels(self, wheel_diameter: float, wheel_width: float, wheel_positions: List[Dict[str, float]]):
        """Add wheels to the vehicle"""
        for pos in wheel_positions:
            # Create wheel cylinder
            wheel_sketch = self.root_comp.sketches.add(self.root_comp.xYConstructionPlane)
            circles = wheel_sketch.sketchCurves.sketchCircles
            center_point = adsk.core.Point3D.create(pos['x'], pos['y'], pos['z'])
            circles.addByCenterRadius(center_point, wheel_diameter / 2)
            
            # Extrude wheel
            profile = wheel_sketch.profiles.item(0)
            extrudes = self.root_comp.features.extrudeFeatures
            ext_input = extrudes.createInput(
                profile,
                adsk.fusion.FeatureOperations.NewBodyFeatureOperation
            )
            ext_input.setDistanceExtent(
                False,
                adsk.core.ValueInput.createByReal(wheel_width)
            )
            extrudes.add(ext_input)

    def add_solar_panels(self, solar_config: Dict):
        """Add solar panels to the vehicle roof"""
        panel_sketch = self.root_comp.sketches.add(self.root_comp.xYConstructionPlane)
        rectangles = panel_sketch.sketchCurves.sketchLines
        
        for panel in solar_config['layout']:
            start = adsk.core.Point3D.create(
                panel['position']['x'],
                panel['position']['y'],
                panel['position']['z']
            )
            rectangles.addTwoPointRectangle(
                start,
                adsk.core.Point3D.create(
                    start.x + panel['dimensions']['length'],
                    start.y + panel['dimensions']['width'],
                    start.z
                )
            )

    def add_battery_compartment(self, battery_config: Dict):
        """Add battery compartment to the vehicle"""
        battery_sketch = self.root_comp.sketches.add(self.root_comp.xYConstructionPlane)
        rectangles = battery_sketch.sketchCurves.sketchLines
        
        start = adsk.core.Point3D.create(
            battery_config['position']['x'],
            battery_config['position']['y'],
            battery_config['position']['z']
        )
        rectangles.addTwoPointRectangle(
            start,
            adsk.core.Point3D.create(
                start.x + battery_config['dimensions']['length'],
                start.y + battery_config['dimensions']['width'],
                start.z
            )
        )

    def export_model(self, export_path: str, file_format: str = 'f3d'):
        """Export the model in specified format"""
        export_mgr = self.app.exportManager
        export_options = export_mgr.createFusionArchiveExportOptions(
            export_path
        )
        export_mgr.execute(export_options)
