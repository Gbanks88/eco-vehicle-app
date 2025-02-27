import json
import platform
import psutil
import cpuinfo
from datetime import datetime
import pymongo
from pymongo import MongoClient

class MongoExporter:
    def __init__(self, connection_string="mongodb://localhost:27017/"):
        self.client = MongoClient(connection_string)
        self.db = self.client['system_monitor']
        
    def get_system_info(self):
        """Collect current system information"""
        cpu_info = cpuinfo.get_cpu_info()
        memory = psutil.virtual_memory()
        disk = psutil.disk_usage('/')
        
        return {
            "timestamp": datetime.utcnow(),
            "system": {
                "os": platform.system(),
                "release": platform.release(),
                "version": platform.version(),
                "machine": platform.machine(),
                "processor": platform.processor(),
                "python_version": platform.python_version()
            },
            "hardware": {
                "cpu": {
                    "brand": cpu_info['brand_raw'],
                    "architecture": cpu_info['arch'],
                    "bits": cpu_info['bits'],
                    "cores": psutil.cpu_count(logical=False),
                    "threads": psutil.cpu_count(logical=True),
                    "usage_percent": psutil.cpu_percent(interval=1)
                },
                "memory": {
                    "total": memory.total,
                    "available": memory.available,
                    "used": memory.used,
                    "percent": memory.percent
                },
                "disk": {
                    "total": disk.total,
                    "used": disk.used,
                    "free": disk.free,
                    "percent": disk.percent
                }
            }
        }

    def get_os_comparison(self):
        """OS comparison data for AI training"""
        return {
            "os_comparison": {
                "windows": {
                    "name": "Windows",
                    "pros": [
                        "Versatile with wide application support",
                        "Strong gaming and enterprise support",
                        "High hardware compatibility",
                        "Regular updates",
                        "Strong customer support"
                    ],
                    "cons": [
                        "Malware vulnerability",
                        "Disruptive updates",
                        "Resource intensive",
                        "Privacy concerns"
                    ],
                    "use_cases": [
                        "Gaming",
                        "Enterprise",
                        "General computing",
                        "Software development"
                    ],
                    "market_share": 75.0,
                    "security_rating": 7.5
                },
                "macos": {
                    "name": "macOS",
                    "pros": [
                        "Excellent build quality",
                        "Apple ecosystem integration",
                        "Strong privacy and security",
                        "User-friendly interface",
                        "Creative professional tools"
                    ],
                    "cons": [
                        "Limited to Apple hardware",
                        "Expensive",
                        "Less customizable",
                        "Limited gaming support"
                    ],
                    "use_cases": [
                        "Creative work",
                        "Professional use",
                        "Software development",
                        "Content creation"
                    ],
                    "market_share": 15.0,
                    "security_rating": 9.0
                },
                "linux": {
                    "name": "Linux",
                    "pros": [
                        "Open-source",
                        "Highly customizable",
                        "Secure and stable",
                        "Free to use",
                        "Strong community support"
                    ],
                    "cons": [
                        "Steep learning curve",
                        "Limited software support",
                        "Hardware compatibility issues",
                        "Complex configuration"
                    ],
                    "use_cases": [
                        "Servers",
                        "Development",
                        "Security",
                        "Education"
                    ],
                    "market_share": 2.0,
                    "security_rating": 9.5
                },
                "chrome_os": {
                    "name": "Chrome OS",
                    "pros": [
                        "Lightweight and fast",
                        "Secure with frequent updates",
                        "Google services integration",
                        "Affordable hardware"
                    ],
                    "cons": [
                        "Limited offline capabilities",
                        "Limited desktop applications",
                        "Google ecosystem dependency",
                        "Limited customization"
                    ],
                    "use_cases": [
                        "Web browsing",
                        "Education",
                        "Basic computing",
                        "Cloud-based work"
                    ],
                    "market_share": 1.5,
                    "security_rating": 8.5
                }
            },
            "mobile_os": {
                "ios": {
                    "name": "iOS",
                    "pros": [
                        "Smooth user experience",
                        "Strong app support",
                        "Robust security",
                        "Regular updates",
                        "Apple ecosystem integration"
                    ],
                    "cons": [
                        "Limited to Apple devices",
                        "Less customization",
                        "Expensive hardware",
                        "Closed ecosystem"
                    ],
                    "use_cases": [
                        "Mobile computing",
                        "Professional use",
                        "Content consumption",
                        "Photography"
                    ],
                    "market_share": 25.0,
                    "security_rating": 9.0
                },
                "android": {
                    "name": "Android",
                    "pros": [
                        "Highly customizable",
                        "Wide device range",
                        "Google services integration",
                        "Large app selection"
                    ],
                    "cons": [
                        "Inconsistent updates",
                        "Malware risks",
                        "Bloatware issues",
                        "Fragmentation"
                    ],
                    "use_cases": [
                        "Mobile computing",
                        "Customization",
                        "Budget devices",
                        "Development"
                    ],
                    "market_share": 70.0,
                    "security_rating": 7.0
                }
            }
        }

    def export_training_data(self):
        """Export system info and OS comparison data for AI training"""
        collection = self.db['ai_training_data']
        
        # Combine system info and OS comparison data
        data = {
            "timestamp": datetime.utcnow(),
            "system_info": self.get_system_info(),
            **self.get_os_comparison()
        }
        
        # Add metadata for training
        data["metadata"] = {
            "data_version": "1.0",
            "source": "system_monitor",
            "purpose": "AI training",
            "categories": [
                "operating_systems",
                "system_monitoring",
                "performance_analysis",
                "compatibility"
            ],
            "features": [
                "system_specs",
                "os_comparison",
                "performance_metrics",
                "usage_patterns"
            ]
        }
        
        # Insert into MongoDB
        result = collection.insert_one(data)
        return result.inserted_id

def main():
    # Initialize exporter
    exporter = MongoExporter()
    
    try:
        # Export data
        doc_id = exporter.export_training_data()
        print(f"Successfully exported training data. Document ID: {doc_id}")
        
        # Export as JSON file as well
        data = exporter.get_system_info()
        with open('system_info.json', 'w') as f:
            json.dump(data, f, default=str, indent=2)
        print("Exported system info to system_info.json")
        
    except Exception as e:
        print(f"Error exporting data: {e}")
    finally:
        exporter.client.close()

if __name__ == "__main__":
    main()
