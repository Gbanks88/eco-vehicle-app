#!/usr/bin/env python3

import os
import requests
import json
import base64
import logging
from pathlib import Path
from dotenv import load_dotenv

class AutodeskAPI:
    def __init__(self):
        load_dotenv()
        self.setup_logging()
        self.client_id = os.getenv('AUTODESK_CLIENT_ID')
        self.client_secret = os.getenv('AUTODESK_CLIENT_SECRET')
        self.base_url = 'https://developer.api.autodesk.com'
        self.token = None
        
    def setup_logging(self):
        """Setup logging configuration"""
        log_dir = Path(__file__).resolve().parents[3] / "logs"
        log_dir.mkdir(exist_ok=True)
        
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(log_dir / "autodesk_api.log"),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger("AutodeskAPI")

    def authenticate(self):
        """Get authentication token"""
        try:
            url = f"{self.base_url}/authentication/v1/authenticate"
            data = {
                'client_id': self.client_id,
                'client_secret': self.client_secret,
                'grant_type': 'client_credentials',
                'scope': 'data:read data:write data:create bucket:create bucket:read'
            }
            response = requests.post(url, data=data)
            response.raise_for_status()
            self.token = response.json()['access_token']
            self.logger.info("Successfully authenticated with Autodesk")
            return True
        except Exception as e:
            self.logger.error(f"Authentication failed: {str(e)}")
            return False

    def create_bucket(self, bucket_key):
        """Create a bucket for storing models"""
        try:
            url = f"{self.base_url}/oss/v2/buckets"
            headers = {
                'Authorization': f'Bearer {self.token}',
                'Content-Type': 'application/json'
            }
            data = {
                'bucketKey': bucket_key,
                'policyKey': 'transient'  # Files deleted after 24 hours
            }
            response = requests.post(url, headers=headers, json=data)
            response.raise_for_status()
            self.logger.info(f"Created bucket: {bucket_key}")
            return response.json()
        except Exception as e:
            self.logger.error(f"Failed to create bucket: {str(e)}")
            return None

    def upload_file(self, bucket_key, file_path):
        """Upload a file to bucket"""
        try:
            file_name = os.path.basename(file_path)
            url = f"{self.base_url}/oss/v2/buckets/{bucket_key}/objects/{file_name}"
            headers = {
                'Authorization': f'Bearer {self.token}',
                'Content-Type': 'application/octet-stream'
            }
            with open(file_path, 'rb') as f:
                response = requests.put(url, headers=headers, data=f)
            response.raise_for_status()
            self.logger.info(f"Uploaded file: {file_name}")
            return response.json()
        except Exception as e:
            self.logger.error(f"Failed to upload file: {str(e)}")
            return None

    def translate_file(self, urn, output_format='dwg'):
        """Translate file to different format"""
        try:
            url = f"{self.base_url}/modelderivative/v2/designdata/job"
            headers = {
                'Authorization': f'Bearer {self.token}',
                'Content-Type': 'application/json'
            }
            data = {
                'input': {
                    'urn': base64.b64encode(urn.encode()).decode()
                },
                'output': {
                    'formats': [{
                        'type': 'design',
                        'advanced': {
                            'exportFileStructure': 'single'
                        },
                        'format': output_format
                    }]
                }
            }
            response = requests.post(url, headers=headers, json=data)
            response.raise_for_status()
            self.logger.info(f"Started translation job for: {urn}")
            return response.json()
        except Exception as e:
            self.logger.error(f"Failed to start translation: {str(e)}")
            return None

    def check_translation_status(self, urn):
        """Check translation job status"""
        try:
            encoded_urn = base64.b64encode(urn.encode()).decode()
            url = f"{self.base_url}/modelderivative/v2/designdata/{encoded_urn}/manifest"
            headers = {
                'Authorization': f'Bearer {self.token}'
            }
            response = requests.get(url, headers=headers)
            response.raise_for_status()
            status = response.json()['status']
            self.logger.info(f"Translation status for {urn}: {status}")
            return status
        except Exception as e:
            self.logger.error(f"Failed to check translation status: {str(e)}")
            return None

    def download_translated_file(self, urn, output_path):
        """Download translated file"""
        try:
            encoded_urn = base64.b64encode(urn.encode()).decode()
            url = f"{self.base_url}/modelderivative/v2/designdata/{encoded_urn}/manifest"
            headers = {
                'Authorization': f'Bearer {self.token}'
            }
            response = requests.get(url, headers=headers)
            response.raise_for_status()
            
            # Get derivative URL
            derivatives = response.json()['derivatives']
            if derivatives and 'outputUrl' in derivatives[0]:
                download_url = derivatives[0]['outputUrl']
                
                # Download file
                response = requests.get(download_url, headers=headers)
                response.raise_for_status()
                
                with open(output_path, 'wb') as f:
                    f.write(response.content)
                    
                self.logger.info(f"Downloaded file to: {output_path}")
                return True
            return False
        except Exception as e:
            self.logger.error(f"Failed to download file: {str(e)}")
            return False

def main():
    # Initialize API
    api = AutodeskAPI()
    
    # Check for credentials
    if not api.client_id or not api.client_secret:
        print("Please set AUTODESK_CLIENT_ID and AUTODESK_CLIENT_SECRET in .env file")
        print("Get these from: https://forge.autodesk.com/")
        return
    
    # Authenticate
    if not api.authenticate():
        return
    
    # Create bucket
    bucket_key = 'eco_vehicle_bucket_' + os.urandom(4).hex()
    bucket_response = api.create_bucket(bucket_key)
    if not bucket_response:
        return
    
    # Upload DXF file
    file_path = Path(__file__).resolve().parents[3] / "outputs/cad/eco_vehicle.dxf"
    upload_response = api.upload_file(bucket_key, str(file_path))
    if not upload_response:
        return
    
    # Start translation
    urn = upload_response['objectId']
    translation_response = api.translate_file(urn, 'dwg')
    if not translation_response:
        return
    
    # Check status until complete
    import time
    while True:
        status = api.check_translation_status(urn)
        if status == 'success':
            break
        elif status in ['failed', 'timeout']:
            print(f"Translation failed with status: {status}")
            return
        time.sleep(5)
    
    # Download result
    output_path = Path(__file__).resolve().parents[3] / "outputs/cad/eco_vehicle.dwg"
    if api.download_translated_file(urn, str(output_path)):
        print(f"Successfully converted DXF to DWG: {output_path}")

if __name__ == "__main__":
    main()
