from ibm_watson_machine_learning import APIClient
import os

class WatsonConfig:
    def __init__(self):
        self.wml_credentials = {
            "url": "https://us-south.ml.cloud.ibm.com",
            "apikey": os.getenv("IBM_CLOUD_API_KEY")
        }
        
    def get_client(self):
        """Initialize and return Watson ML client"""
        client = APIClient(self.wml_credentials)
        return client
    
    def setup_space(self, space_name="eco_vehicle_ml"):
        """Create or get ML space"""
        client = self.get_client()
        spaces = client.spaces.get_details()
        space_id = None
        
        # Find existing space or create new one
        for space in spaces['resources']:
            if space['entity']['name'] == space_name:
                space_id = space['metadata']['id']
                break
        
        if not space_id:
            space = client.spaces.store(
                {
                    'name': space_name,
                    'description': 'Space for eco-vehicle ML models',
                    'type': 'cpd'
                }
            )
            space_id = space['metadata']['id']
        
        return space_id

    def deploy_model(self, model_path, space_id):
        """Deploy PyTorch model to Watson ML"""
        client = self.get_client()
        client.set.default_space(space_id)
        
        # Software specification for PyTorch
        software_spec_uid = client.software_specifications.get_id_by_name("pytorch_2.0")
        
        model_details = {
            'name': 'eco_vehicle_model',
            'type': 'pytorch_2.0',
            'software_spec_uid': software_spec_uid
        }
        
        return client.repository.store_model(
            model=model_path,
            meta_props=model_details
        )
