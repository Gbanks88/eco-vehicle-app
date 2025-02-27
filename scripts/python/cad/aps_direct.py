#!/usr/bin/env python3

import os
import requests
import json
import time
import base64
from pathlib import Path
from dotenv import load_dotenv

def main():
    # Load environment variables
    load_dotenv()
    
    # Get credentials
    client_id = os.getenv('AUTODESK_CLIENT_ID')
    client_secret = os.getenv('AUTODESK_CLIENT_SECRET')
    
    # Get authentication token
    auth_url = 'https://developer.api.autodesk.com/authentication/v2/token'
    auth_data = {
        'client_id': client_id,
        'client_secret': client_secret,
        'grant_type': 'client_credentials',
        'scope': 'data:read data:write data:create bucket:create bucket:read'
    }
    
    print("Getting authentication token...")
    auth_response = requests.post(auth_url, data=auth_data)
    auth_response.raise_for_status()
    access_token = auth_response.json()['access_token']
    
    # Headers for subsequent requests
    headers = {
        'Authorization': f'Bearer {access_token}',
        'Content-Type': 'application/json'
    }
    
    # Create a bucket
    bucket_key = f'ecovehicle{os.urandom(4).hex()}'
    bucket_url = 'https://developer.api.autodesk.com/oss/v2/buckets'
    bucket_data = {
        'bucketKey': bucket_key,
        'policyKey': 'transient'
    }
    
    print(f"Creating bucket: {bucket_key}")
    bucket_response = requests.post(bucket_url, headers=headers, json=bucket_data)
    bucket_response.raise_for_status()
    
    # Upload the DXF file using signed URLs
    file_path = Path(__file__).resolve().parents[3] / "outputs/cad/eco_vehicle.dxf"
    object_name = os.path.basename(file_path)
    
    # Get signed URL for upload
    signed_url = f'https://developer.api.autodesk.com/oss/v2/buckets/{bucket_key}/objects/{object_name}/signeds3upload'
    
    print(f"Getting signed URL for upload: {object_name}")
    signed_response = requests.get(signed_url, headers=headers)
    signed_response.raise_for_status()
    signed_data = signed_response.json()
    
    # Upload to S3
    print(f"Uploading file: {object_name}")
    with open(file_path, 'rb') as f:
        upload_response = requests.put(
            signed_data['urls'][0],
            data=f,
            headers={'Content-Type': 'application/octet-stream'}
        )
        upload_response.raise_for_status()
    
    # Complete upload
    complete_data = {'uploadKey': signed_data['uploadKey']}
    complete_response = requests.post(signed_url, headers=headers, json=complete_data)
    complete_response.raise_for_status()
    
    object_id = f'urn:adsk.objects:os.object:{bucket_key}/{object_name}'
    
    # Prepare for translation
    urn = base64.b64encode(object_id.encode()).decode()
    translate_url = 'https://developer.api.autodesk.com/modelderivative/v2/designdata/job'
    translate_data = {
        'input': {
            'urn': urn,
            'compressedUrn': False,
            'rootFilename': object_name
        },
        'output': {
            'formats': [
                {
                    'type': 'svf',
                    'views': ['2d', '3d']
                }
            ]
        }
    }
    
    print("Starting translation...")
    translate_response = requests.post(
        translate_url,
        headers=headers,
        json=translate_data
    )
    translate_response.raise_for_status()
    
    # Check translation status
    manifest_url = f'https://developer.api.autodesk.com/modelderivative/v2/designdata/{urn}/manifest'
    print("\nChecking translation status...")
    
    while True:
        manifest_response = requests.get(manifest_url, headers=headers)
        manifest_response.raise_for_status()
        manifest = manifest_response.json()
        
        if manifest.get('status') == 'success':
            print("Translation completed!")
            break
        elif manifest.get('status') in ['failed', 'timeout']:
            print(f"Translation failed with status: {manifest.get('status')}")
            return
        
        print(".", end="", flush=True)
        time.sleep(5)
    
    # Get the SVF derivative
    derivatives = manifest.get('derivatives', [])
    for derivative in derivatives:
        if derivative.get('outputType') == 'svf':
            for geometry in derivative.get('children', []):
                if geometry.get('role') == '2d':
                    for resource in geometry.get('children', []):
                        if resource.get('role') == 'graphics':
                            download_url = f'https://developer.api.autodesk.com/derivativeservice/v2/derivatives/{resource["urn"]}'
                            output_path = Path(__file__).resolve().parents[3] / "outputs/cad/eco_vehicle_converted.f2d"
                            
                            print(f"\nDownloading F2D file to: {output_path}")
                            download_response = requests.get(download_url, headers=headers)
                            download_response.raise_for_status()
                            
                            with open(output_path, 'wb') as f:
                                f.write(download_response.content)
                            
                            print("Successfully downloaded F2D file!")
                            return
    
    print("No F2D derivative found in the manifest")

if __name__ == '__main__':
    main()
