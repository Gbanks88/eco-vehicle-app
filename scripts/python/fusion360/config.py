"""
Configuration settings for Fusion 360 integration
"""
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class FusionConfig:
    # API Configuration
    API_VERSION = os.getenv('FUSION_API_VERSION', 'v1')
    BASE_URL = os.getenv('FUSION_BASE_URL', 'https://developer.api.autodesk.com/fusion360')
    
    # File formats supported for export
    SUPPORTED_FORMATS = {
        'stl': '.stl',
        'step': '.step',
        'iges': '.igs',
        'sat': '.sat',
        'smt': '.smt'
    }
    
    # Default paths
    DEFAULT_SAVE_PATH = os.path.expanduser('~/Documents/Fusion360Projects')
    
    @staticmethod
    def get_export_path(filename: str, format_type: str) -> str:
        """Generate full export path with proper extension"""
        if format_type.lower() not in FusionConfig.SUPPORTED_FORMATS:
            raise ValueError(f"Unsupported format: {format_type}")
            
        extension = FusionConfig.SUPPORTED_FORMATS[format_type.lower()]
        if not filename.endswith(extension):
            filename += extension
            
        return os.path.join(FusionConfig.DEFAULT_SAVE_PATH, filename)

# Car blueprint dimensions in millimeters
CAR_DIMENSIONS = {
    # Main body dimensions
    'body_length': 4800,  # Length of the car
    'body_width': 1850,   # Width of the car
    'body_height': 1400,  # Height of the car
    
    # Wheelbase and track
    'wheelbase': 2850,    # Distance between front and rear axles
    'front_track': 1600,  # Distance between front wheels
    'rear_track': 1600,   # Distance between rear wheels
    
    # Wheel dimensions
    'wheel_radius': 350,  # Wheel radius including tire
    'wheel_width': 245,   # Tire width
    
    # Ground clearance
    'ground_clearance': 150,  # Height from ground to lowest point
    
    # Engine compartment
    'engine_length': 800,   # Length of engine bay
    'engine_width': 700,    # Width of engine bay
    'engine_height': 500,   # Height of engine bay
    
    # Interior dimensions
    'cabin_length': 2000,   # Length of passenger cabin
    'cabin_width': 1500,    # Width of passenger cabin
    'cabin_height': 1200,   # Height of passenger cabin
    
    # Aerodynamic features
    'front_overhang': 950,  # Distance from front axle to front bumper
    'rear_overhang': 1000,  # Distance from rear axle to rear bumper
    'drag_coefficient': 0.32,  # Aerodynamic drag coefficient
    
    # Performance specs
    'weight': 1800,         # Vehicle weight in kg
    'power': 500,          # Engine power in HP
    'torque': 480,         # Engine torque in lb-ft
    'top_speed': 180,      # Top speed in mph
    'acceleration': 3.8,    # 0-60 mph time in seconds
}
