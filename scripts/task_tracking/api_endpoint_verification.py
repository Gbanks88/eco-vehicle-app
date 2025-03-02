"""
API Endpoint Verification Script
Verifies the status and functionality of API endpoints
"""

import requests
import json
from datetime import datetime
from typing import Dict, List, Optional
from enum import Enum

class EndpointMethod(Enum):
    GET = "GET"
    POST = "POST"
    PUT = "PUT"
    DELETE = "DELETE"

class ApiEndpointVerification:
    def __init__(self):
        self.base_url = "https://api.cg4f.online"
        self.endpoints = {
            "/products": {
                "methods": [EndpointMethod.GET, EndpointMethod.POST],
                "auth_required": True
            },
            "/products/{id}": {
                "methods": [EndpointMethod.GET, EndpointMethod.PUT, EndpointMethod.DELETE],
                "auth_required": True
            },
            "/cart": {
                "methods": [EndpointMethod.GET, EndpointMethod.POST],
                "auth_required": True
            },
            "/orders": {
                "methods": [EndpointMethod.GET, EndpointMethod.POST],
                "auth_required": True
            },
            "/auth/login": {
                "methods": [EndpointMethod.POST],
                "auth_required": False
            },
            "/auth/register": {
                "methods": [EndpointMethod.POST],
                "auth_required": False
            }
        }
    
    def get_auth_token(self) -> Optional[str]:
        """Get authentication token for testing"""
        try:
            response = requests.post(
                f"{self.base_url}/auth/login",
                json={"email": "test@example.com", "password": "test123"}
            )
            if response.status_code == 200:
                return response.json().get("token")
        except:
            pass
        return None
    
    def verify_endpoint(self, path: str, method: EndpointMethod, auth_required: bool) -> Dict:
        """Verify single endpoint functionality"""
        url = f"{self.base_url}{path}"
        headers = {}
        
        if auth_required:
            token = self.get_auth_token()
            if token:
                headers["Authorization"] = f"Bearer {token}"
        
        try:
            if method == EndpointMethod.GET:
                response = requests.get(url, headers=headers)
            elif method == EndpointMethod.POST:
                response = requests.post(url, headers=headers, json={})
            elif method == EndpointMethod.PUT:
                response = requests.put(url, headers=headers, json={})
            else:  # DELETE
                response = requests.delete(url, headers=headers)
            
            return {
                "status_code": response.status_code,
                "status": "Valid" if response.status_code < 500 else "Error",
                "response": response.json() if response.status_code < 500 else None
            }
        except Exception as e:
            return {
                "status": "Error",
                "error": str(e)
            }
    
    def verify_all_endpoints(self) -> Dict:
        """Verify all configured endpoints"""
        results = {}
        for path, config in self.endpoints.items():
            path_results = {}
            for method in config["methods"]:
                path_results[method.value] = self.verify_endpoint(
                    path, 
                    method, 
                    config["auth_required"]
                )
            results[path] = path_results
        
        return results
    
    def verify_cors(self) -> Dict:
        """Verify CORS configuration"""
        try:
            headers = {
                "Origin": "https://cg4f.online"
            }
            response = requests.options(f"{self.base_url}/products", headers=headers)
            
            cors_headers = {
                "Access-Control-Allow-Origin": headers["Origin"],
                "Access-Control-Allow-Methods": "GET,POST,PUT,DELETE",
                "Access-Control-Allow-Headers": "Content-Type,Authorization"
            }
            
            cors_status = {}
            for header, expected in cors_headers.items():
                actual = response.headers.get(header)
                cors_status[header] = {
                    "present": actual is not None,
                    "value": actual,
                    "expected": expected,
                    "status": "Valid" if actual == expected else "Invalid"
                }
            
            return {
                "status": "Valid" if all(c["status"] == "Valid" for c in cors_status.values()) else "Invalid",
                "headers": cors_status
            }
        except Exception as e:
            return {"status": "Error", "error": str(e)}
    
    def generate_report(self) -> Dict:
        """Generate API endpoint verification report"""
        endpoint_results = self.verify_all_endpoints()
        cors_results = self.verify_cors()
        
        # Calculate overall status
        endpoints_valid = all(
            result["status"] == "Valid"
            for path_results in endpoint_results.values()
            for method_results in path_results.values()
            for result in [method_results]
        )
        
        report = {
            "timestamp": datetime.now().isoformat(),
            "base_url": self.base_url,
            "endpoints": endpoint_results,
            "cors_configuration": cors_results,
            "overall_status": "Completed" if endpoints_valid and cors_results["status"] == "Valid" else "Issues Found"
        }
        
        # Save report
        with open("api_endpoint_report.json", "w") as f:
            json.dump(report, f, indent=2)
        
        return report

if __name__ == "__main__":
    verifier = ApiEndpointVerification()
    report = verifier.generate_report()
    print(f"API Endpoint Status: {report['overall_status']}")
    
    if report['overall_status'] != "Completed":
        print("\nIssues found:")
        for path, methods in report['endpoints'].items():
            for method, result in methods.items():
                if result["status"] != "Valid":
                    print(f"- {method} {path}: {result.get('error', 'Invalid response')}")
        if report['cors_configuration']['status'] != "Valid":
            print("- CORS configuration issues detected")
