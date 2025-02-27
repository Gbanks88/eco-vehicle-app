"""
Example usage of the Fusion 360 integration
"""
import os
from fusion_client import FusionClient
from config import FusionConfig

def main():
    # Initialize the Fusion client
    client = FusionClient()
    
    try:
        # Connect to Fusion 360
        if not client.initialize():
            print("Failed to initialize Fusion 360 connection")
            return

        # Create a new design
        design_name = "Example_Design"
        design = client.create_new_design(design_name)
        if not design:
            print("Failed to create new design")
            return
        
        # Save the design
        save_path = os.path.join(FusionConfig.DEFAULT_SAVE_PATH, f"{design_name}.f3d")
        if client.save_design(save_path):
            print(f"Design saved successfully to: {save_path}")
        else:
            print("Failed to save design")
            
        # Export to different formats
        for format_type in ['stl', 'step']:
            export_path = FusionConfig.get_export_path(design_name, format_type)
            if client.export_design(export_path, format_type):
                print(f"Design exported successfully to: {export_path}")
            else:
                print(f"Failed to export design to {format_type}")

    except Exception as e:
        print(f"An error occurred: {str(e)}")

if __name__ == '__main__':
    main()
