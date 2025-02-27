#!/usr/bin/env python3

import math
from pyautocad import Autocad, APoint
import logging
from pathlib import Path

class VehicleDesigner:
    def __init__(self):
        self.acad = Autocad()
        self.setup_logging()
        
    def setup_logging(self):
        """Setup logging configuration"""
        log_dir = Path(__file__).resolve().parents[3] / "logs"
        log_dir.mkdir(exist_ok=True)
        
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(log_dir / "vehicle_designer.log"),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger("VehicleDesigner")

    def draw_chassis(self, length=4500, width=1800, height=1500):
        """Draw vehicle chassis with dimensions in mm"""
        try:
            # Base rectangle (top view)
            points = [
                APoint(0, 0),
                APoint(length, 0),
                APoint(length, width),
                APoint(0, width),
                APoint(0, 0)
            ]
            
            # Draw base rectangle
            self.acad.model.AddPolyline(points)
            
            # Add wheelbase
            wheelbase = length * 0.6
            front_axle = length * 0.2
            rear_axle = front_axle + wheelbase
            
            # Draw axle lines
            self.acad.model.AddLine(
                APoint(front_axle, 0),
                APoint(front_axle, width)
            )
            self.acad.model.AddLine(
                APoint(rear_axle, 0),
                APoint(rear_axle, width)
            )
            
            self.logger.info(f"Drew chassis: {length}x{width}x{height}mm")
            return True
            
        except Exception as e:
            self.logger.error(f"Error drawing chassis: {str(e)}")
            return False

    def draw_wheels(self, wheel_radius=350):
        """Draw wheels with given radius in mm"""
        try:
            # Get chassis dimensions from current drawing
            length = 4500  # Default length if not found
            width = 1800   # Default width if not found
            
            wheelbase = length * 0.6
            front_axle = length * 0.2
            rear_axle = front_axle + wheelbase
            track_width = width * 0.8
            
            # Draw wheels (circles)
            wheel_positions = [
                APoint(front_axle, width * 0.1),  # Front left
                APoint(front_axle, width * 0.9),  # Front right
                APoint(rear_axle, width * 0.1),   # Rear left
                APoint(rear_axle, width * 0.9)    # Rear right
            ]
            
            for pos in wheel_positions:
                self.acad.model.AddCircle(pos, wheel_radius)
            
            self.logger.info(f"Drew wheels with radius: {wheel_radius}mm")
            return True
            
        except Exception as e:
            self.logger.error(f"Error drawing wheels: {str(e)}")
            return False

    def draw_powertrain(self, motor_size=300):
        """Draw electric powertrain components"""
        try:
            # Get chassis dimensions
            length = 4500  # Default length if not found
            width = 1800   # Default width if not found
            
            # Draw motor (simplified as rectangle)
            motor_pos = APoint(length * 0.4, width * 0.4)
            motor_points = [
                motor_pos,
                APoint(motor_pos.x + motor_size, motor_pos.y),
                APoint(motor_pos.x + motor_size, motor_pos.y + motor_size),
                APoint(motor_pos.x, motor_pos.y + motor_size),
                motor_pos
            ]
            self.acad.model.AddPolyline(motor_points)
            
            # Draw battery pack (simplified as rectangle)
            battery_length = length * 0.4
            battery_width = width * 0.6
            battery_pos = APoint(length * 0.3, width * 0.2)
            battery_points = [
                battery_pos,
                APoint(battery_pos.x + battery_length, battery_pos.y),
                APoint(battery_pos.x + battery_length, battery_pos.y + battery_width),
                APoint(battery_pos.x, battery_pos.y + battery_width),
                battery_pos
            ]
            self.acad.model.AddPolyline(battery_points)
            
            self.logger.info("Drew powertrain components")
            return True
            
        except Exception as e:
            self.logger.error(f"Error drawing powertrain: {str(e)}")
            return False

    def add_dimensions(self):
        """Add dimensions to the drawing"""
        try:
            # Get chassis dimensions
            length = 4500  # Default length if not found
            width = 1800   # Default width if not found
            
            # Add overall length dimension
            self.acad.model.AddDimAligned(
                APoint(0, -200),
                APoint(length, -200),
                APoint(length/2, -300)
            )
            
            # Add width dimension
            self.acad.model.AddDimAligned(
                APoint(-200, 0),
                APoint(-200, width),
                APoint(-300, width/2)
            )
            
            # Add wheelbase dimension
            wheelbase = length * 0.6
            front_axle = length * 0.2
            self.acad.model.AddDimAligned(
                APoint(front_axle, -400),
                APoint(front_axle + wheelbase, -400),
                APoint(front_axle + wheelbase/2, -500)
            )
            
            self.logger.info("Added dimensions to drawing")
            return True
            
        except Exception as e:
            self.logger.error(f"Error adding dimensions: {str(e)}")
            return False

    def add_annotations(self):
        """Add text annotations to the drawing"""
        try:
            # Get chassis dimensions
            length = 4500  # Default length if not found
            width = 1800   # Default width if not found
            
            # Add title
            self.acad.model.AddText(
                "Eco-Vehicle Technical Drawing",
                APoint(-500, width + 500),
                100
            )
            
            # Add component labels
            self.acad.model.AddText(
                "Electric Motor",
                APoint(length * 0.4, width * 0.3),
                50
            )
            self.acad.model.AddText(
                "Battery Pack",
                APoint(length * 0.3, width * 0.15),
                50
            )
            
            # Add specifications
            specs = [
                "Specifications:",
                "- Overall Length: 4500mm",
                "- Overall Width: 1800mm",
                "- Wheelbase: 2700mm",
                "- Track Width: 1440mm"
            ]
            
            for i, spec in enumerate(specs):
                self.acad.model.AddText(
                    spec,
                    APoint(-500, width + 300 - i*70),
                    40
                )
            
            self.logger.info("Added annotations to drawing")
            return True
            
        except Exception as e:
            self.logger.error(f"Error adding annotations: {str(e)}")
            return False

    def create_complete_drawing(self):
        """Create complete vehicle technical drawing"""
        try:
            # Clear current drawing
            self.acad.doc.New()
            
            # Set up layers
            self.acad.doc.Layers.Add("Chassis")
            self.acad.doc.Layers.Add("Wheels")
            self.acad.doc.Layers.Add("Powertrain")
            self.acad.doc.Layers.Add("Dimensions")
            self.acad.doc.Layers.Add("Annotations")
            
            # Draw components
            self.draw_chassis()
            self.draw_wheels()
            self.draw_powertrain()
            self.add_dimensions()
            self.add_annotations()
            
            # Save drawing
            save_path = Path(__file__).resolve().parents[3] / "outputs/cad"
            save_path.mkdir(parents=True, exist_ok=True)
            self.acad.doc.SaveAs(str(save_path / "eco_vehicle.dwg"))
            
            self.logger.info("Created complete vehicle drawing")
            return True
            
        except Exception as e:
            self.logger.error(f"Error creating complete drawing: {str(e)}")
            return False

def main():
    designer = VehicleDesigner()
    designer.create_complete_drawing()

if __name__ == "__main__":
    main()
