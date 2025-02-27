#!/usr/bin/env python3

import os
import requests
import json
import base64
import logging
import time
from pathlib import Path
from dotenv import load_dotenv

class APSManager:
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
                logging.FileHandler(log_dir / "aps.log"),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger("APSManager")

    def authenticate(self):
        """Get APS authentication token"""
        try:
            url = f"{self.base_url}/authentication/v2/token"
            data = {
                'client_id': self.client_id,
                'client_secret': self.client_secret,
                'grant_type': 'client_credentials',
                'scope': 'data:read data:write data:create bucket:create bucket:read bucket:delete'
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
            if response.status_code == 409:  # Bucket already exists
                self.logger.info(f"Bucket {bucket_key} already exists")
                return {'bucketKey': bucket_key}
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
            
            # Get the upload URL
            url = f"{self.base_url}/oss/v2/buckets/{bucket_key}/objects/{file_name}/signeds3upload"
            headers = {
                'Authorization': f'Bearer {self.token}'
            }
            response = requests.get(url, headers=headers)
            response.raise_for_status()
            upload_info = response.json()
            
            # Upload to S3
            with open(file_path, 'rb') as f:
                response = requests.put(
                    upload_info['urls'][0],
                    data=f,
                    headers={
                        'Content-Type': 'application/octet-stream'
                    }
                )
                response.raise_for_status()
            
            # Complete the upload
            url = f"{self.base_url}/oss/v2/buckets/{bucket_key}/objects/{file_name}/signeds3upload"
            complete_data = {
                'uploadKey': upload_info['uploadKey']
            }
            response = requests.post(url, headers=headers, json=complete_data)
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
                'Content-Type': 'application/json',
                'x-ads-force': 'true'  # Force translation even if output already exists
            }
            
            # Ensure URN is properly base64 encoded
            if not urn.startswith('urn:'):
                urn = f'urn:adsk.objects:os.object:{urn}'
            encoded_urn = base64.b64encode(urn.encode()).decode()
            
            data = {
                'input': {
                    'urn': encoded_urn,
                    'compressedUrn': False,
                    'rootFilename': 'eco_vehicle.dxf'
                },
                'output': {
                    'formats': [{
                        'type': 'svf',
                        'views': ['2d', '3d']
                    }]
                }
            }
            response = requests.post(url, headers=headers, json=data)
            self.logger.info(f"Translation request data: {json.dumps(data, indent=2)}")
            self.logger.info(f"Translation response: {response.text}")
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

    def download_derivative(self, urn, output_path):
        """Download the translated file"""
        try:
            encoded_urn = base64.b64encode(urn.encode()).decode()
            url = f"{self.base_url}/modelderivative/v2/designdata/{encoded_urn}/manifest"
            headers = {
                'Authorization': f'Bearer {self.token}'
            }
            
            # Get manifest
            response = requests.get(url, headers=headers)
            response.raise_for_status()
            manifest = response.json()
            
            # For SVF format, we need to get the manifest details
            derivatives = manifest.get('derivatives', [])
            if not derivatives:
                self.logger.error("No derivatives found in manifest")
                return False

            # Print available derivatives for debugging
            self.logger.info(f"Available derivatives: {json.dumps(derivatives, indent=2)}")
            
            # For SVF, we typically want the F2D (2D) or SVF (3D) derivative
            f2d_items = []
            for derivative in derivatives:
                if derivative.get('outputType', '') == 'svf':
                    for geom in derivative.get('children', []):
                        if geom.get('type') == 'geometry' and geom.get('role') == '2d':
                            for child in geom.get('children', []):
                                if child.get('role') == 'graphics' and child.get('mime') == 'application/autodesk-f2d':
                                    f2d_items.append({
                                        'type': 'f2d',
                                        'role': child.get('role', ''),
                                        'urn': child['urn']
                                    })
            
            if not f2d_items:
                self.logger.error("No F2D derivatives found")
                return False
            
            # Log available F2D items
            self.logger.info(f"Available F2D items: {json.dumps(f2d_items, indent=2)}")
            
            # Get the first F2D item
            f2d_item = f2d_items[0]
            derivative_url = f"{self.base_url}/derivativeservice/v2/derivatives/{f2d_item['urn']}"
            
            # Download file
            response = requests.get(derivative_url, headers=headers)
            response.raise_for_status()
            
            with open(output_path, 'wb') as f:
                f.write(response.content)
            
            self.logger.info(f"Downloaded {f2d_item['type']} derivative to: {output_path}")
            return True
        except Exception as e:
            self.logger.error(f"Failed to download file: {str(e)}")
            return False

def main():
    # Initialize manager
    manager = APSManager()
    
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
    
    # Wait for file to be processed
    print("\nWaiting for file to be processed...")
    time.sleep(5)
    
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
    
    # Download the converted file
    output_path = Path(__file__).resolve().parents[3] / "outputs/cad/eco_vehicle_converted.dwg"
    if manager.download_derivative(urn, str(output_path)):
        print(f"\nSuccessfully converted and downloaded file to: {output_path}")
    else:
        print("\nFailed to download converted file")

if __name__ == "__main__":
    main()
