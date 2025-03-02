"""
Netlify Configuration Verification Script
Verifies the Netlify deployment configuration
"""

import os
import toml
import json
from datetime import datetime

class NetlifyConfigVerification:
    def __init__(self):
        self.required_configs = {
            "build": {
                "command": "npm run build",
                "publish": ".next"
            },
            "plugins": ["@netlify/plugin-nextjs"]
        }
    
    def verify_toml_config(self):
        """Verify netlify.toml configuration"""
        try:
            if not os.path.exists("netlify.toml"):
                return {"status": "Missing", "error": "netlify.toml not found"}
            
            config = toml.load("netlify.toml")
            
            # Check build settings
            build_status = {
                "command_match": config.get("build", {}).get("command") == self.required_configs["build"]["command"],
                "publish_match": config.get("build", {}).get("publish") == self.required_configs["build"]["publish"]
            }
            
            # Check plugins
            plugins = [p.get("package") for p in config.get("plugins", [])]
            plugins_status = {
                "nextjs_plugin": "@netlify/plugin-nextjs" in plugins
            }
            
            return {
                "status": "Valid" if all(build_status.values()) and all(plugins_status.values()) else "Invalid",
                "build_configuration": build_status,
                "plugins_configuration": plugins_status
            }
        except Exception as e:
            return {"status": "Error", "error": str(e)}
    
    def verify_dependencies(self):
        """Verify required Netlify dependencies in package.json"""
        try:
            if not os.path.exists("package.json"):
                return {"status": "Missing", "error": "package.json not found"}
            
            with open("package.json", "r") as f:
                package = json.load(f)
            
            dev_deps = package.get("devDependencies", {})
            deps = package.get("dependencies", {})
            all_deps = {**dev_deps, **deps}
            
            required_deps = {
                "@netlify/plugin-nextjs": "present" in all_deps
            }
            
            return {
                "status": "Valid" if all(required_deps.values()) else "Missing Dependencies",
                "dependencies": required_deps
            }
        except Exception as e:
            return {"status": "Error", "error": str(e)}
    
    def generate_report(self):
        """Generate Netlify configuration verification report"""
        toml_status = self.verify_toml_config()
        deps_status = self.verify_dependencies()
        
        report = {
            "timestamp": datetime.now().isoformat(),
            "netlify_toml": toml_status,
            "dependencies": deps_status,
            "overall_status": "Completed" if toml_status["status"] == "Valid" and 
                            deps_status["status"] == "Valid" else "Configuration Issues"
        }
        
        # Save report
        with open("netlify_config_report.json", "w") as f:
            json.dump(report, f, indent=2)
        
        return report

if __name__ == "__main__":
    verifier = NetlifyConfigVerification()
    report = verifier.generate_report()
    print(f"Netlify Configuration Status: {report['overall_status']}")
    
    if report['overall_status'] != "Completed":
        print("\nConfiguration issues found:")
        if report['netlify_toml']['status'] != "Valid":
            print("- Issues with netlify.toml configuration")
        if report['dependencies']['status'] != "Valid":
            print("- Missing required dependencies")
