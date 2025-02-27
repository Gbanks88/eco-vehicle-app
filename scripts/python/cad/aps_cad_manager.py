#!/usr/bin/env python3

import os
import requests
import json
import base64
import logging
import time
from pathlib import Path
from dotenv import load_dotenv

class APSCADManager:
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
                logging.FileHandler(log_dir / "aps_cad.log"),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger("APSCADManager")

    def authenticate(self):
        """Get APS authentication token"""
        try:
            url = f"{self.base_url}/authentication/v2/token"
            data = {
                'client_id': self.client_id,
                'client_secret': self.client_secret,
                'grant_type': 'client_credentials',
                'scope': 'data:read data:write data:create bucket:create bucket:read bucket:delete account:read account:write'
            }
            response = requests.post(url, data=data)
            response.raise_for_status()
            self.token = response.json()['access_token']
            self.logger.info("Successfully authenticated with APS")
            return True
        except Exception as e:
            self.logger.error(f"Authentication failed: {str(e)}")
            return False

    def create_bucket(self, bucket_key):
        """Create a bucket for storing models"""
        try:
            url = f"{self.base_url}/oss/v2/buckets"  # This endpoint is still valid
            headers = {
                'Authorization': f'Bearer {self.token}',
                'Content-Type': 'application/json'
            }
            data = {
                'bucketKey': bucket_key,
                'policyKey': 'transient'
            }
            response = requests.post(url, headers=headers, json=data)
            response.raise_for_status()
            self.logger.info(f"Created bucket: {bucket_key}")
            return response.json()
        except requests.exceptions.HTTPError as e:
            if e.response.status_code == 409:  # Bucket already exists
                self.logger.info(f"Bucket {bucket_key} already exists")
                return {'bucketKey': bucket_key}
            else:
                self.logger.error(f"Failed to create bucket: {str(e)}")
                return None
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
            self.logger.info(f"Uploading file {file_path} to {url}")
            file_size = os.path.getsize(file_path)
            self.logger.info(f"File size: {file_size} bytes")
            
            with open(file_path, 'rb') as f:
                self.logger.info("File opened successfully")
                response = requests.put(url, headers=headers, data=f)
                self.logger.info(f"Upload response status: {response.status_code}")
                self.logger.info(f"Upload response: {response.text}")
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
            status = response.json()
            self.logger.info(f"Translation status: {status.get('status')}")
            return status
        except Exception as e:
            self.logger.error(f"Failed to check translation status: {str(e)}")
            return None

    def get_derivative_url(self, urn, derivative_urn=None):
        """Get URL for downloading the translated file"""
        try:
            encoded_urn = base64.b64encode(urn.encode()).decode()
            url = f"{self.base_url}/modelderivative/v2/designdata/{encoded_urn}/manifest"
            headers = {
                'Authorization': f'Bearer {self.token}'
            }
            response = requests.get(url, headers=headers)
            response.raise_for_status()
            manifest = response.json()
            
            if not derivative_urn and 'derivatives' in manifest:
                for derivative in manifest['derivatives']:
                    if 'outputUrl' in derivative:
                        return derivative['outputUrl']
                    for child in derivative.get('children', []):
                        if 'outputUrl' in child:
                            return child['outputUrl']
            return None
        except Exception as e:
            self.logger.error(f"Failed to get derivative URL: {str(e)}")
            return None

    def download_file(self, url, output_path):
        """Download a file from APS"""
        try:
            headers = {
                'Authorization': f'Bearer {self.token}'
            }
            response = requests.get(url, headers=headers)
            response.raise_for_status()
            
            with open(output_path, 'wb') as f:
                f.write(response.content)
            
            self.logger.info(f"Downloaded file to: {output_path}")
            return True
        except Exception as e:
            self.logger.error(f"Failed to download file: {str(e)}")
            return False

def main():
    # Initialize manager
    manager = APSCADManager()
    
    # Authenticate
    if not manager.authenticate():
        return
    
    # Create bucket
    bucket_key = 'ecovehicle' + os.urandom(4).hex().lower()
    bucket_response = manager.create_bucket(bucket_key)
    if not bucket_response:
        return
    
    # Upload DXF file
    file_path = Path(__file__).resolve().parents[3] / "outputs/cad/eco_vehicle.dxf"
    upload_response = manager.upload_file(bucket_key, str(file_path))
    if not upload_response:
        return
    
    # Start translation
    urn = upload_response['objectId']
    translation_response = manager.translate_file(urn, 'dwg')
    if not translation_response:
        return
    
    # Wait for translation to complete
    print("\nWaiting for translation to complete...")
    while True:
        status = manager.check_translation_status(urn)
        if not status:
            return
        
        if status['status'] == 'success':
            print("Translation completed successfully!")
            break
        elif status['status'] in ['failed', 'timeout']:
            print(f"Translation failed with status: {status['status']}")
            return
        
        print(".", end="", flush=True)
        time.sleep(5)
    
    # Get download URL
    download_url = manager.get_derivative_url(urn)
    if not download_url:
        print("Failed to get download URL")
        return
    
    # Download the converted file
    output_path = Path(__file__).resolve().parents[3] / "outputs/cad/eco_vehicle_converted.dwg"
    if manager.download_file(download_url, str(output_path)):
        print(f"\nSuccessfully converted and downloaded file to: {output_path}")
    else:
        print("\nFailed to download converted file")

if __name__ == "__main__":
    main()
