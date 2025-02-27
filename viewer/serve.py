#!/usr/bin/env python3

import os
import json
from http.server import HTTPServer, SimpleHTTPRequestHandler
from dotenv import load_dotenv
import requests
import base64

# Load environment variables
load_dotenv()

class ViewerHandler(SimpleHTTPRequestHandler):
    def do_GET(self):
        if self.path == '/token':
            self.send_token()
        else:
            # Serve static files
            super().do_GET()
    
    def send_token(self):
        try:
            # Get token from Autodesk
            client_id = os.getenv('AUTODESK_CLIENT_ID')
            client_secret = os.getenv('AUTODESK_CLIENT_SECRET')
            
            url = 'https://developer.api.autodesk.com/authentication/v2/token'
            data = {
                'client_id': client_id,
                'client_secret': client_secret,
                'grant_type': 'client_credentials',
                'scope': 'viewables:read'
            }
            
            response = requests.post(url, data=data)
            response.raise_for_status()
            
            # Send token to client
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            self.wfile.write(response.content)
            
        except Exception as e:
            self.send_error(500, str(e))

def run_server(port=8000):
    server_address = ('', port)
    httpd = HTTPServer(server_address, ViewerHandler)
    print(f"Server running on port {port}...")
    httpd.serve_forever()

if __name__ == '__main__':
    run_server()
