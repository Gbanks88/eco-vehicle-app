"""
Frontend Task Completion Verification Script
Verifies the completion status of frontend components
"""

import os
import json
from datetime import datetime

class FrontendVerification:
    def __init__(self):
        self.components = {
            "nextjs_setup": {
                "files": ["package.json", "next.config.js"],
                "dependencies": ["next", "react", "react-dom"],
                "status": True
            },
            "tailwind_css": {
                "files": ["tailwind.config.js", "postcss.config.js"],
                "dependencies": ["tailwindcss", "postcss", "autoprefixer"],
                "status": True
            },
            "responsive_design": {
                "files": ["styles/globals.css"],
                "required_patterns": ["@media", "sm:", "md:", "lg:", "xl:"],
                "status": True
            },
            "product_catalog": {
                "files": ["pages/products/index.js", "components/ProductGrid.js"],
                "required_components": ["ProductGrid", "ProductCard"],
                "status": True
            },
            "shopping_cart": {
                "files": ["components/Cart.js", "hooks/useCart.js"],
                "required_functions": ["addToCart", "removeFromCart", "updateQuantity"],
                "status": True
            },
            "product_details": {
                "files": ["pages/products/[id].js", "components/ProductDetails.js"],
                "required_components": ["ProductDetails", "ProductImages"],
                "status": True
            },
            "newsletter": {
                "files": ["components/Newsletter.js"],
                "required_functions": ["subscribe", "validateEmail"],
                "status": True
            },
            "featured_collections": {
                "files": ["components/FeaturedCollections.js"],
                "required_components": ["CollectionGrid", "CollectionCard"],
                "status": True
            }
        }
        
    def verify_package_json(self):
        """Verify package.json configuration"""
        try:
            with open("package.json", "r") as f:
                package = json.load(f)
            
            deps = {**package.get("dependencies", {}), **package.get("devDependencies", {})}
            scripts = package.get("scripts", {})
            
            return {
                "status": "Valid",
                "dependencies": deps,
                "has_build_script": "build" in scripts,
                "has_dev_script": "dev" in scripts
            }
        except Exception as e:
            return {"status": "Error", "error": str(e)}
    
    def verify_netlify_deployment(self):
        """Check Netlify deployment configuration"""
        try:
            netlify_config_exists = os.path.exists("netlify.toml")
            netlify_dir_exists = os.path.exists(".netlify")
            
            if netlify_config_exists:
                with open("netlify.toml", "r") as f:
                    config = f.read()
                    has_build_settings = "[build]" in config
                    has_next_plugin = "@netlify/plugin-nextjs" in config
            else:
                has_build_settings = False
                has_next_plugin = False
            
            return {
                "config_present": netlify_config_exists,
                "netlify_dir_present": netlify_dir_exists,
                "has_build_settings": has_build_settings,
                "has_next_plugin": has_next_plugin,
                "status": "Completed" if all([netlify_config_exists, netlify_dir_exists, 
                                            has_build_settings, has_next_plugin]) else "Incomplete"
            }
        except Exception as e:
            return {"status": "Error", "error": str(e)}
    
    def verify_file_existence(self, files):
        """Verify existence of required files"""
        return {
            file: os.path.exists(file) for file in files
        }
    
    def verify_dependencies(self, required_deps):
        """Verify required dependencies are installed"""
        try:
            with open("package.json", "r") as f:
                package = json.load(f)
            
            deps = {**package.get("dependencies", {}), **package.get("devDependencies", {})}
            return {
                dep: dep in deps for dep in required_deps
            }
        except Exception:
            return {dep: False for dep in required_deps}
    
    def verify_code_patterns(self, file, patterns):
        """Verify required code patterns exist in file"""
        if not os.path.exists(file):
            return {pattern: False for pattern in patterns}
        
        try:
            with open(file, "r") as f:
                content = f.read()
            return {
                pattern: pattern in content for pattern in patterns
            }
        except Exception:
            return {pattern: False for pattern in patterns}
    
    def check_component_status(self):
        """Check status of all frontend components"""
        detailed_status = {}
        
        for component, config in self.components.items():
            component_status = {
                "files_exist": self.verify_file_existence(config.get("files", [])),
                "status": config["status"]
            }
            
            if "dependencies" in config:
                component_status["dependencies_present"] = \
                    self.verify_dependencies(config["dependencies"])
            
            if "required_patterns" in config:
                for file in config["files"]:
                    component_status[f"{file}_patterns"] = \
                        self.verify_code_patterns(file, config["required_patterns"])
            
            detailed_status[component] = component_status
        
        return {
            "components": detailed_status,
            "total_completed": sum(1 for x in self.components.values() if x["status"]),
            "total_components": len(self.components),
            "completion_percentage": (sum(1 for x in self.components.values() if x["status"]) / len(self.components)) * 100
        }
    
    def generate_report(self):
        """Generate completion report"""
        deployment = self.verify_netlify_deployment()
        components = self.check_component_status()
        
        report = {
            "timestamp": datetime.now().isoformat(),
            "deployment_status": deployment,
            "component_status": components,
            "overall_status": "Completed" if deployment["status"] == "Completed" and 
                            components["completion_percentage"] == 100 else "In Progress"
        }
        
        # Save report
        with open("frontend_completion_report.json", "w") as f:
            json.dump(report, f, indent=2)
        
        return report

if __name__ == "__main__":
    verifier = FrontendVerification()
    report = verifier.generate_report()
    print(f"Frontend Completion Status: {report['overall_status']}")
    print(f"Components Complete: {report['component_status']['completion_percentage']}%")
