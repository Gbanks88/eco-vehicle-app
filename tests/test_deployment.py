import requests
import json
import socketio
import time
import os

class DeploymentTester:
    def __init__(self, base_url):
        self.base_url = base_url
        self.sio = socketio.Client()
        self.test_results = {}

    def test_health_endpoint(self):
        """Test the health check endpoint"""
        try:
            response = requests.get(f"{self.base_url}/health")
            assert response.status_code == 200
            data = response.json()
            assert data['status'] == 'healthy'
            self.test_results['health_check'] = 'PASS'
        except Exception as e:
            self.test_results['health_check'] = f'FAIL: {str(e)}'

    def test_forge_viewer(self):
        """Test the 3D viewer page loads"""
        try:
            response = requests.get(f"{self.base_url}/vehicle_viewer")
            assert response.status_code == 200
            assert 'Forge Viewer' in response.text
            self.test_results['forge_viewer'] = 'PASS'
        except Exception as e:
            self.test_results['forge_viewer'] = f'FAIL: {str(e)}'

    def test_websocket(self):
        """Test WebSocket connection"""
        try:
            @self.sio.event
            def connect():
                self.test_results['websocket_connect'] = 'PASS'

            @self.sio.event
            def connect_error(data):
                self.test_results['websocket_connect'] = f'FAIL: Connection error'

            self.sio.connect(self.base_url)
            time.sleep(2)  # Wait for connection
            self.sio.disconnect()
        except Exception as e:
            self.test_results['websocket_connect'] = f'FAIL: {str(e)}'

    def test_recycling_game(self):
        """Test recycling game endpoints"""
        try:
            response = requests.get(f"{self.base_url}/recycling_game")
            assert response.status_code == 200
            self.test_results['recycling_game'] = 'PASS'
        except Exception as e:
            self.test_results['recycling_game'] = f'FAIL: {str(e)}'

    def run_all_tests(self):
        """Run all deployment tests"""
        print("Starting deployment tests...")
        
        # Run tests
        self.test_health_endpoint()
        self.test_forge_viewer()
        self.test_websocket()
        self.test_recycling_game()

        # Print results
        print("\nTest Results:")
        print("=" * 50)
        for test, result in self.test_results.items():
            print(f"{test}: {result}")
        print("=" * 50)

if __name__ == "__main__":
    # Get the deployment URL from environment or use default
    deployment_url = os.getenv("DEPLOYMENT_URL", "https://eco-vehicle-app.onrender.com")
    
    # Run tests
    tester = DeploymentTester(deployment_url)
    tester.run_all_tests()
