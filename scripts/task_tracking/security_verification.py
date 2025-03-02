"""
Security Configuration Verification Script
Verifies security headers, CSP, and other security configurations
"""

import requests
import json
from datetime import datetime
from typing import Dict, List, Optional

class SecurityVerification:
    def __init__(self):
        self.required_headers = {
            "X-Frame-Options": "DENY",
            "X-Content-Type-Options": "nosniff",
            "Referrer-Policy": "strict-origin-when-cross-origin",
            "Strict-Transport-Security": "max-age=31536000; includeSubDomains; preload"
        }
        self.required_csp_directives = [
            "default-src",
            "script-src",
            "style-src",
            "img-src",
            "connect-src"
        ]
    
    def verify_security_headers(self, url: str) -> Dict:
        """Verify security headers are properly configured"""
        try:
            response = requests.get(url)
            headers = response.headers
            
            header_status = {}
            for header, expected_value in self.required_headers.items():
                actual_value = headers.get(header)
                header_status[header] = {
                    "present": actual_value is not None,
                    "value": actual_value,
                    "expected": expected_value,
                    "status": "Valid" if actual_value == expected_value else "Invalid"
                }
            
            return {
                "status": "Valid" if all(h["status"] == "Valid" for h in header_status.values()) else "Invalid",
                "headers": header_status
            }
        except Exception as e:
            return {"status": "Error", "error": str(e)}
    
    def verify_csp(self, url: str) -> Dict:
        """Verify Content Security Policy configuration"""
        try:
            response = requests.get(url)
            csp_header = response.headers.get("Content-Security-Policy")
            
            if not csp_header:
                return {"status": "Missing", "error": "CSP header not found"}
            
            directives = {}
            for directive in csp_header.split(";"):
                directive = directive.strip()
                if directive:
                    parts = directive.split()
                    directives[parts[0]] = parts[1:]
            
            # Check required directives
            directive_status = {}
            for required in self.required_csp_directives:
                directive_status[required] = {
                    "present": required in directives,
                    "value": directives.get(required, []),
                    "status": "Valid" if required in directives else "Missing"
                }
            
            return {
                "status": "Valid" if all(d["status"] == "Valid" for d in directive_status.values()) else "Invalid",
                "directives": directive_status
            }
        except Exception as e:
            return {"status": "Error", "error": str(e)}
    
    def verify_permissions_policy(self, url: str) -> Dict:
        """Verify Permissions-Policy header configuration"""
        try:
            response = requests.get(url)
            policy = response.headers.get("Permissions-Policy")
            
            if not policy:
                return {"status": "Missing", "error": "Permissions-Policy header not found"}
            
            required_restrictions = ["camera", "microphone", "geolocation"]
            restrictions = {}
            
            for directive in policy.split(","):
                directive = directive.strip()
                if directive:
                    name = directive.split("=")[0]
                    value = directive.split("=")[1] if "=" in directive else ""
                    restrictions[name] = value
            
            restriction_status = {}
            for required in required_restrictions:
                restriction_status[required] = {
                    "present": required in restrictions,
                    "value": restrictions.get(required, ""),
                    "status": "Valid" if required in restrictions else "Missing"
                }
            
            return {
                "status": "Valid" if all(r["status"] == "Valid" for r in restriction_status.values()) else "Invalid",
                "restrictions": restriction_status
            }
        except Exception as e:
            return {"status": "Error", "error": str(e)}
    
    def generate_report(self, url: str) -> Dict:
        """Generate security verification report"""
        headers_status = self.verify_security_headers(url)
        csp_status = self.verify_csp(url)
        permissions_status = self.verify_permissions_policy(url)
        
        report = {
            "timestamp": datetime.now().isoformat(),
            "url": url,
            "security_headers": headers_status,
            "content_security_policy": csp_status,
            "permissions_policy": permissions_status,
            "overall_status": "Completed" if all(s["status"] == "Valid" for s in 
                [headers_status, csp_status, permissions_status]) else "Issues Found"
        }
        
        # Save report
        with open("security_verification_report.json", "w") as f:
            json.dump(report, f, indent=2)
        
        return report

if __name__ == "__main__":
    verifier = SecurityVerification()
    url = "https://cg4f.online"  # Replace with your domain
    report = verifier.generate_report(url)
    print(f"Security Configuration Status: {report['overall_status']}")
    
    if report['overall_status'] != "Completed":
        print("\nSecurity issues found:")
        if report['security_headers']['status'] != "Valid":
            print("- Security headers misconfigured")
        if report['content_security_policy']['status'] != "Valid":
            print("- Content Security Policy issues")
        if report['permissions_policy']['status'] != "Valid":
            print("- Permissions Policy misconfigured")
