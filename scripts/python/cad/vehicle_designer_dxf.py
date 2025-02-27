#!/usr/bin/env python3

import ezdxf
import math
import logging
from pathlib import Path

class VehicleDesignerDXF:
    def __init__(self):
        self.doc = ezdxf.new('R2018')
        self.msp = self.doc.modelspace()
        self.setup_logging()
        self.setup_layers()
        
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
        self.logger = logging.getLogger("VehicleDesignerDXF")

    def setup_layers(self):
        """Setup drawing layers"""
        layers = ['Chassis', 'Wheels', 'Powertrain', 'Dimensions', 'Annotations']
        for layer_name in layers:
            self.doc.layers.add(layer_name)

    def draw_chassis(self, length=4500, width=1800, height=1500):
        """Draw vehicle chassis with dimensions in mm"""
        try:
            # Set current layer
            self.doc.layers.get('Chassis').is_on = True
            
            # Base rectangle (top view)
            points = [
                (0, 0), (length, 0),
                (length, width), (0, width),
                (0, 0)
            ]
            
            # Draw base rectangle
            self.msp.add_lwpolyline(points, dxfattribs={'layer': 'Chassis'})
            
            # Add wheelbase
            wheelbase = length * 0.6
            front_axle = length * 0.2
            rear_axle = front_axle + wheelbase
            
            # Draw axle lines
            self.msp.add_line(
                (front_axle, 0),
                (front_axle, width),
                dxfattribs={'layer': 'Chassis'}
            )
            self.msp.add_line(
                (rear_axle, 0),
                (rear_axle, width),
                dxfattribs={'layer': 'Chassis'}
            )
            
            self.logger.info(f"Drew chassis: {length}x{width}x{height}mm")
            return True
            
        except Exception as e:
            self.logger.error(f"Error drawing chassis: {str(e)}")
            return False

    def draw_wheels(self, wheel_radius=350):
        """Draw wheels with given radius in mm"""
        try:
            self.doc.layers.get('Wheels').is_on = True
            
            # Get chassis dimensions
            length = 4500  # Default length if not found
            width = 1800   # Default width if not found
            
            wheelbase = length * 0.6
            front_axle = length * 0.2
            rear_axle = front_axle + wheelbase
            
            # Draw wheels (circles)
            wheel_positions = [
                (front_axle, width * 0.1),  # Front left
                (front_axle, width * 0.9),  # Front right
                (rear_axle, width * 0.1),   # Rear left
                (rear_axle, width * 0.9)    # Rear right
            ]
            
            for x, y in wheel_positions:
                self.msp.add_circle(
                    (x, y),
                    wheel_radius,
                    dxfattribs={'layer': 'Wheels'}
                )
            
            self.logger.info(f"Drew wheels with radius: {wheel_radius}mm")
            return True
            
        except Exception as e:
            self.logger.error(f"Error drawing wheels: {str(e)}")
            return False

    def draw_powertrain(self, motor_size=300):
        """Draw electric powertrain components"""
        try:
            self.doc.layers.get('Powertrain').is_on = True
            
            # Get chassis dimensions
            length = 4500  # Default length if not found
            width = 1800   # Default width if not found
            
            # Draw motor (simplified as rectangle)
            motor_x = length * 0.4
            motor_y = width * 0.4
            motor_points = [
                (motor_x, motor_y),
                (motor_x + motor_size, motor_y),
                (motor_x + motor_size, motor_y + motor_size),
                (motor_x, motor_y + motor_size),
                (motor_x, motor_y)
            ]
            self.msp.add_lwpolyline(
                motor_points,
                dxfattribs={'layer': 'Powertrain'}
            )
            
            # Draw battery pack (simplified as rectangle)
            battery_length = length * 0.4
            battery_width = width * 0.6
            battery_x = length * 0.3
            battery_y = width * 0.2
            battery_points = [
                (battery_x, battery_y),
                (battery_x + battery_length, battery_y),
                (battery_x + battery_length, battery_y + battery_width),
                (battery_x, battery_y + battery_width),
                (battery_x, battery_y)
            ]
            self.msp.add_lwpolyline(
                battery_points,
                dxfattribs={'layer': 'Powertrain'}
            )
            
            self.logger.info("Drew powertrain components")
            return True
            
        except Exception as e:
            self.logger.error(f"Error drawing powertrain: {str(e)}")
            return False

    def add_dimensions(self):
        """Add dimensions to the drawing"""
        try:
            self.doc.layers.get('Dimensions').is_on = True
            
            # Get chassis dimensions
            length = 4500  # Default length if not found
            width = 1800   # Default width if not found
            
            # Add overall length dimension
            self.msp.add_linear_dim(
                (0, -200),
                (length, -200),
                (-300, -200),
                dimstyle='EZDXF',
                override={'dimtxt': 100},
                dxfattribs={'layer': 'Dimensions'}
            )
            
            # Add width dimension
            self.msp.add_linear_dim(
                (-200, 0),
                (-200, width),
                (-200, -100),
                dimstyle='EZDXF',
                override={'dimtxt': 100},
                dxfattribs={'layer': 'Dimensions'}
            )
            
            # Add wheelbase dimension
            wheelbase = length * 0.6
            front_axle = length * 0.2
            self.msp.add_linear_dim(
                (front_axle, -400),
                (front_axle + wheelbase, -400),
                (-500, -400),
                dimstyle='EZDXF',
                override={'dimtxt': 100},
                dxfattribs={'layer': 'Dimensions'}
            )
            
            self.logger.info("Added dimensions to drawing")
            return True
            
        except Exception as e:
            self.logger.error(f"Error adding dimensions: {str(e)}")
            return False

    def add_annotations(self):
        """Add text annotations to the drawing"""
        try:
            self.doc.layers.get('Annotations').is_on = True
            
            # Get chassis dimensions
            length = 4500  # Default length if not found
            width = 1800   # Default width if not found
            
            # Add title
            self.msp.add_text(
                "Eco-Vehicle Technical Drawing",
                dxfattribs={
                    'layer': 'Annotations',
                    'height': 100,
                    'insert': (-500, width + 500)
                }
            )
            
            # Add component labels
            self.msp.add_text(
                "Electric Motor",
                dxfattribs={
                    'layer': 'Annotations',
                    'height': 50,
                    'insert': (length * 0.4, width * 0.3)
                }
            )
            self.msp.add_text(
                "Battery Pack",
                dxfattribs={
                    'layer': 'Annotations',
                    'height': 50,
                    'insert': (length * 0.3, width * 0.15)
                }
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
                self.msp.add_text(
                    spec,
                    dxfattribs={
                        'layer': 'Annotations',
                        'height': 40,
                        'insert': (-500, width + 300 - i*70)
                    }
                )
            
            self.logger.info("Added annotations to drawing")
            return True
            
        except Exception as e:
            self.logger.error(f"Error adding annotations: {str(e)}")
            return False

    def create_complete_drawing(self):
        """Create complete vehicle technical drawing"""
        try:
            # Draw components
            self.draw_chassis()
            self.draw_wheels()
            self.draw_powertrain()
            self.add_dimensions()
            self.add_annotations()
            
            # Save drawing
            save_path = Path(__file__).resolve().parents[3] / "outputs/cad"
            save_path.mkdir(parents=True, exist_ok=True)
            self.doc.saveas(str(save_path / "eco_vehicle.dxf"))
            
            self.logger.info("Created complete vehicle drawing")
            return True
            
        except Exception as e:
            self.logger.error(f"Error creating complete drawing: {str(e)}")
            return False

def main():
    designer = VehicleDesignerDXF()
    designer.create_complete_drawing()

if __name__ == "__main__":
    main()
