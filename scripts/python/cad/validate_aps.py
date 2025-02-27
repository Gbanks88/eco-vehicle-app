#!/usr/bin/env python3

import os
import requests
from dotenv import load_dotenv

def validate_aps_auth():
    # Load environment variables
    load_dotenv()
    
    client_id = os.getenv('AUTODESK_CLIENT_ID')
    client_secret = os.getenv('AUTODESK_CLIENT_SECRET')
    
    if not client_id or not client_secret:
        print("❌ Error: Missing credentials in .env file")
        return False
    
    # Use the new APS authentication endpoint
    url = "https://developer.api.autodesk.com/authentication/v2/token"
    data = {
        'client_id': client_id,
        'client_secret': client_secret,
        'grant_type': 'client_credentials',
        'scope': 'viewables:read'  # Basic scope for testing
    }
    
    try:
        print("Attempting authentication with APS credentials:")
        print(f"Client ID: {client_id[:5]}...{client_id[-5:]}")
        print(f"Client Secret: {client_secret[:5]}...{client_secret[-5:]}")
        
        response = requests.post(url, data=data)
        response.raise_for_status()
        
        # Get token from response
        token = response.json().get('access_token')
        if token:
            print("\n✅ Success: APS authentication successful!")
            print("Token received:", token[:10] + "..." + token[-10:])
            return True
        else:
            print("\n❌ Error: No access token received")
            return False
            
    except requests.exceptions.HTTPError as e:
        print(f"\n❌ Error: Authentication failed with status {e.response.status_code}")
        print("Response:", e.response.text)
        print("\nTroubleshooting steps:")
        print("1. Go to https://aps.autodesk.com/")
        print("2. Sign in and go to 'My Apps'")
        print("3. For your app 'EcoFredilyInnovation':")
        print("   - Enable the required APIs (Data Management, Model Derivative)")
        print("   - Verify the app is active")
        print("   - Check the callback URL is set correctly")
        print("4. Make sure you've accepted the terms of service")
        return False
    except Exception as e:
        print(f"\n❌ Error: {str(e)}")
        return False

if __name__ == "__main__":
    validate_aps_auth()
