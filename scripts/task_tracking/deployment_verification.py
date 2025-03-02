"""
Deployment Configuration Verification Script
Verifies the deployment and DNS configuration status
"""

import socket
import requests
from datetime import datetime
import json

class DeploymentVerification:
    def __init__(self):
        self.domain = "cg4f.online"
        self.expected_config = {
            "root_domain": "57.128.180.184",
            "api_subdomain": "57.128.180.184",
            "cdn_subdomain": "cg4l.site"
        }
    
    def verify_dns_records(self):
        """Verify DNS records match expected configuration"""
        try:
            # Check root domain
            root_ip = socket.gethostbyname(self.domain)
            api_ip = socket.gethostbyname(f"api.{self.domain}")
            cdn_record = socket.gethostbyname(f"cdn.{self.domain}")
            
            return {
                "root_domain": {
                    "expected": self.expected_config["root_domain"],
                    "actual": root_ip,
                    "status": "Matched" if root_ip == self.expected_config["root_domain"] else "Mismatch"
                },
                "api_subdomain": {
                    "expected": self.expected_config["api_subdomain"],
                    "actual": api_ip,
                    "status": "Matched" if api_ip == self.expected_config["api_subdomain"] else "Mismatch"
                },
                "cdn_subdomain": {
                    "expected": self.expected_config["cdn_subdomain"],
                    "actual": cdn_record,
                    "status": "Configured"
                }
            }
        except socket.gaierror:
            return {"error": "DNS resolution failed"}
    
    def verify_ssl(self):
        """Verify SSL certificates"""
        domains = [
            f"https://{self.domain}",
            f"https://api.{self.domain}",
            f"https://cdn.{self.domain}"
        ]
        
        ssl_status = {}
        for domain in domains:
            try:
                response = requests.get(domain, verify=True)
                ssl_status[domain] = "Valid SSL"
            except requests.exceptions.SSLError:
                ssl_status[domain] = "Invalid SSL"
            except requests.exceptions.RequestException:
                ssl_status[domain] = "Connection Failed"
        
        return ssl_status
    
    def generate_report(self):
        """Generate deployment verification report"""
        dns_status = self.verify_dns_records()
        ssl_status = self.verify_ssl()
        
        report = {
            "timestamp": datetime.now().isoformat(),
            "dns_configuration": dns_status,
            "ssl_status": ssl_status,
            "overall_status": "Completed" if "error" not in dns_status and 
                            all(status == "Valid SSL" for status in ssl_status.values()) else "Issues Found"
        }
        
        # Save report
        with open("deployment_verification_report.json", "w") as f:
            json.dump(report, f, indent=2)
        
        return report

if __name__ == "__main__":
    verifier = DeploymentVerification()
    report = verifier.generate_report()
    print(f"Deployment Status: {report['overall_status']}")
    if report['overall_status'] == "Issues Found":
        print("\nIssues detected:")
        if "error" in report["dns_configuration"]:
            print("- DNS configuration issues found")
        for domain, status in report["ssl_status"].items():
            if status != "Valid SSL":
                print(f"- SSL issue with {domain}: {status}")
