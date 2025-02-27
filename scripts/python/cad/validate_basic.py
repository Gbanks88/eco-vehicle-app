#!/usr/bin/env python3

import os
import requests
from dotenv import load_dotenv

def validate_basic_auth():
    # Load environment variables
    load_dotenv()
    
    client_id = os.getenv('AUTODESK_CLIENT_ID')
    client_secret = os.getenv('AUTODESK_CLIENT_SECRET')
    
    if not client_id or not client_secret:
        print("❌ Error: Missing credentials in .env file")
        return False
    
    # Try to authenticate with minimal scope
    url = "https://developer.api.autodesk.com/authentication/v1/authenticate"
    data = {
        'client_id': client_id,
        'client_secret': client_secret,
        'grant_type': 'client_credentials',
        'scope': 'viewables:read'  # Minimal scope for testing
    }
    
    try:
        print("Attempting authentication with credentials:")
        print(f"Client ID: {client_id[:5]}...{client_id[-5:]}")
        print(f"Client Secret: {client_secret[:5]}...{client_secret[-5:]}")
        
        response = requests.post(url, data=data)
        response.raise_for_status()
        
        # Get token from response
        token = response.json().get('access_token')
        if token:
            print("\n✅ Success: Basic authentication successful!")
            print("Token received:", token[:10] + "..." + token[-10:])
            return True
        else:
            print("\n❌ Error: No access token received")
            return False
            
    except requests.exceptions.HTTPError as e:
        print(f"\n❌ Error: Authentication failed with status {e.response.status_code}")
        print("Response:", e.response.text)
        print("\nTroubleshooting steps:")
        print("1. Verify you've enabled the API services in your Forge account")
        print("2. Make sure you've accepted the terms of service")
        print("3. Check if your application is active")
        print("4. Verify your email address is confirmed")
        return False
    except Exception as e:
        print(f"\n❌ Error: {str(e)}")
        return False

if __name__ == "__main__":
    validate_basic_auth()
