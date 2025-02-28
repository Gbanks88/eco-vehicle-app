from flask import Blueprint, jsonify, request
import os
import requests
from datetime import datetime, timedelta

forge_api = Blueprint('forge_api', __name__)

# Cache for the access token
token_cache = {
    'access_token': None,
    'expires_at': None
}

def get_forge_token():
    """Get a new token or return cached token if still valid"""
    global token_cache
    
    now = datetime.now()
    
    # Return cached token if still valid
    if token_cache['access_token'] and token_cache['expires_at'] and now < token_cache['expires_at']:
        return token_cache['access_token']
    
    # Get new token
    client_id = os.environ.get('FORGE_CLIENT_ID')
    client_secret = os.environ.get('FORGE_CLIENT_SECRET')
    
    data = {
        'grant_type': 'client_credentials',
        'scope': 'data:read data:write data:create bucket:read bucket:create'
    }
    
    try:
        response = requests.post(
            'https://developer.api.autodesk.com/authentication/v1/authenticate',
            data=data,
            auth=(client_id, client_secret)
        )
        response.raise_for_status()
        token_data = response.json()
        
        # Cache the token
        token_cache['access_token'] = token_data['access_token']
        token_cache['expires_at'] = now + timedelta(seconds=token_data['expires_in'])
        
        return token_cache['access_token']
    except Exception as e:
        print(f"Error getting Forge token: {str(e)}")
        return None

@forge_api.route('/api/forge/oauth/token', methods=['GET'])
def get_token():
    """Endpoint to get Forge token for the viewer"""
    token = get_forge_token()
    if token:
        return jsonify({
            'access_token': token,
            'expires_in': 3600
        })
    return jsonify({'error': 'Could not get access token'}), 500

@forge_api.route('/api/forge/urn/<string:model_name>', methods=['GET'])
def get_model_urn(model_name):
    """Get the URN for a specific model"""
    # This would typically fetch from a database
    # For now, we'll return a hardcoded URN for testing
    return jsonify({
        'urn': os.environ.get('FORGE_MODEL_URN', 'your-model-urn')
    })

@forge_api.route('/api/forge/models', methods=['GET'])
def list_models():
    """List available models"""
    token = get_forge_token()
    if not token:
        return jsonify({'error': 'Could not authenticate'}), 500
        
    bucket_key = os.environ.get('FORGE_BUCKET_KEY')
    headers = {'Authorization': f'Bearer {token}'}
    
    try:
        response = requests.get(
            f'https://developer.api.autodesk.com/oss/v2/buckets/{bucket_key}/objects',
            headers=headers
        )
        response.raise_for_status()
        return jsonify(response.json())
    except Exception as e:
        return jsonify({'error': str(e)}), 500
