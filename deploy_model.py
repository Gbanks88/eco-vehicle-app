import torch
from watson_config import WatsonConfig
import os

def deploy_pytorch_model():
    # Initialize Watson configuration
    watson = WatsonConfig()
    
    # Create ML space
    space_id = watson.setup_space()
    
    # Example PyTorch model (replace with your actual model)
    class EcoVehicleModel(torch.nn.Module):
        def __init__(self):
            super().__init__()
            self.layers = torch.nn.Sequential(
                torch.nn.Linear(10, 64),
                torch.nn.ReLU(),
                torch.nn.Linear(64, 32),
                torch.nn.ReLU(),
                torch.nn.Linear(32, 1)
            )
            
        def forward(self, x):
            return self.layers(x)
    
    # Create and save model
    model = EcoVehicleModel()
    model_path = "eco_vehicle_model.pt"
    torch.save(model.state_dict(), model_path)
    
    # Deploy to Watson ML
    deployment = watson.deploy_model(model_path, space_id)
    print(f"Model deployed successfully: {deployment}")
    
    # Clean up local file
    os.remove(model_path)

if __name__ == "__main__":
    deploy_pytorch_model()
