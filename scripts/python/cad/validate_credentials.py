#!/usr/bin/env python3

import os
import requests
from dotenv import load_dotenv

def validate_credentials():
    # Load environment variables
    load_dotenv()
    
    client_id = os.getenv('AUTODESK_CLIENT_ID')
    client_secret = os.getenv('AUTODESK_CLIENT_SECRET')
    
    if not client_id or not client_secret:
        print("❌ Error: Missing credentials in .env file")
        return False
    
    # Try to authenticate with Autodesk
    url = "https://developer.api.autodesk.com/authentication/v1/authenticate"
    data = {
        'client_id': client_id,
        'client_secret': client_secret,
        'grant_type': 'client_credentials',
        'scope': 'data:read data:write data:create bucket:create bucket:read'
    }
    
    try:
        response = requests.post(url, data=data)
        response.raise_for_status()
        
        # Get token from response
        token = response.json().get('access_token')
        if token:
            print("✅ Success: Credentials are valid!")
            print("Token received:", token[:10] + "..." + token[-10:])
            return True
        else:
            print("❌ Error: No access token received")
            return False
            
    except requests.exceptions.HTTPError as e:
        print(f"❌ Error: Authentication failed with status {e.response.status_code}")
        print("Response:", e.response.text)
        return False
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        return False

if __name__ == "__main__":
    validate_credentials()
