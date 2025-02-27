import os
import sys
import base64
import requests
from pathlib import Path
from dotenv import load_dotenv

def get_forge_token():
    """Get Forge API access token"""
    client_id = os.environ.get('AUTODESK_CLIENT_ID') or os.environ.get('FORGE_CLIENT_ID')
    client_secret = os.environ.get('AUTODESK_CLIENT_SECRET') or os.environ.get('FORGE_CLIENT_SECRET')
    
    data = {
        'grant_type': 'client_credentials',
        'scope': 'data:read data:write data:create bucket:create bucket:read account:read account:write'
    }
    
    try:
        response = requests.post(
            'https://developer.api.autodesk.com/authentication/v2/token',
            data=data,
            auth=(client_id, client_secret)
        )
        response.raise_for_status()
        return response.json()['access_token']
    except Exception as e:
        print(f"Error getting token: {str(e)}")
        return None

def create_bucket(token, bucket_key):
    """Create a bucket if it doesn't exist"""
    headers = {
        'Authorization': f'Bearer {token}',
        'Content-Type': 'application/json'
    }
    
    data = {
        'bucketKey': bucket_key,
        'policyKey': 'persistent',
        'region': 'us'
    }
    
    try:
        response = requests.post(
            'https://developer.api.autodesk.com/aps/v2/data/buckets',
            headers=headers,
            json=data
        )
        if response.status_code == 409:  # Bucket exists
            return True
        response.raise_for_status()
        return True
    except requests.exceptions.RequestException as e:
        if hasattr(e.response, 'json'):
            error_data = e.response.json()
            print(f"Error creating bucket: {error_data}")
        else:
            print(f"Error creating bucket: {str(e)}")
        return False

def upload_file(token, bucket_key, file_path):
    """Upload a file to Forge"""
    file_name = os.path.basename(file_path)
    
    headers = {
        'Authorization': f'Bearer {token}',
        'Content-Type': 'application/octet-stream'
    }
    
    try:
        with open(file_path, 'rb') as f:
            response = requests.put(
                f'https://developer.api.autodesk.com/aps/v2/data/buckets/{bucket_key}/objects/{file_name}',
                headers=headers,
                data=f
            )
        response.raise_for_status()
        return response.json()['objectId']
    except requests.exceptions.RequestException as e:
        if hasattr(e.response, 'json'):
            error_data = e.response.json()
            print(f"Error uploading file: {error_data}")
        else:
            print(f"Error uploading file: {str(e)}")
        return None

def translate_file(token, object_id):
    """Translate the file for viewing"""
    headers = {
        'Authorization': f'Bearer {token}',
        'Content-Type': 'application/json'
    }
    
    data = {
        'input': {
            'urn': base64.b64encode(object_id.encode()).decode('utf-8')
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
    
    try:
        response = requests.post(
            'https://developer.api.autodesk.com/modelderivative/v2/designdata/job',
            headers=headers,
            json=data
        )
        response.raise_for_status()
        return base64.b64encode(object_id.encode()).decode('utf-8')
    except Exception as e:
        print(f"Error translating file: {str(e)}")
        return None

def main():
    if len(sys.argv) != 2:
        print("Usage: python upload_model.py <path_to_model_file>")
        sys.exit(1)
    
    load_dotenv()
    file_path = sys.argv[1]
    bucket_key = os.environ.get('FORGE_BUCKET_KEY')
    
    if not os.path.exists(file_path):
        print(f"File not found: {file_path}")
        sys.exit(1)
    
    print("Getting Forge token...")
    token = get_forge_token()
    if not token:
        print("Failed to get token")
        sys.exit(1)
    
    print(f"Creating bucket {bucket_key}...")
    if not create_bucket(token, bucket_key):
        print("Failed to create bucket")
        sys.exit(1)
    
    print("Uploading file...")
    object_id = upload_file(token, bucket_key, file_path)
    if not object_id:
        print("Failed to upload file")
        sys.exit(1)
    
    print("Translating file...")
    urn = translate_file(token, object_id)
    if not urn:
        print("Failed to translate file")
        sys.exit(1)
    
    print("\nSuccess!")
    print(f"Model URN: {urn}")
    print("\nAdd this URN to your environment variables:")
    print(f"FORGE_MODEL_URN={urn}")

if __name__ == '__main__':
    main()
