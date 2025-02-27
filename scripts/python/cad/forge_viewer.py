#!/usr/bin/env python3

from autodesk_forge import ForgeClient
import os
import json
import logging
from pathlib import Path

class ForgeViewer:
    def __init__(self):
        self.setup_logging()
        self.client_id = os.getenv('FORGE_CLIENT_ID')
        self.client_secret = os.getenv('FORGE_CLIENT_SECRET')
        self.bucket_key = 'eco_vehicle_bucket'
        
    def setup_logging(self):
        log_dir = Path(__file__).resolve().parents[3] / "logs"
        log_dir.mkdir(exist_ok=True)
        
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(log_dir / "forge_viewer.log"),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger("ForgeViewer")

    def authenticate(self):
        """Authenticate with Forge"""
        try:
            self.forge = ForgeClient(
                client_id=self.client_id,
                client_secret=self.client_secret
            )
            self.logger.info("Successfully authenticated with Forge")
            return True
        except Exception as e:
            self.logger.error(f"Authentication failed: {str(e)}")
            return False

    def create_bucket(self):
        """Create a bucket for storing models"""
        try:
            response = self.forge.create_bucket(
                bucket_key=self.bucket_key,
                policy_key='transient'  # Files deleted after 24 hours
            )
            self.logger.info(f"Created bucket: {self.bucket_key}")
            return response
        except Exception as e:
            self.logger.error(f"Failed to create bucket: {str(e)}")
            return None

    def upload_model(self, file_path):
        """Upload a model to Forge"""
        try:
            with open(file_path, 'rb') as f:
                response = self.forge.upload_object(
                    bucket_key=self.bucket_key,
                    object_key=os.path.basename(file_path),
                    object_content=f
                )
            self.logger.info(f"Uploaded model: {file_path}")
            return response
        except Exception as e:
            self.logger.error(f"Failed to upload model: {str(e)}")
            return None

    def translate_model(self, urn):
        """Translate the model for viewing"""
        try:
            response = self.forge.translate_model(
                urn=urn,
                target_format='svf',
                force=True
            )
            self.logger.info(f"Started model translation: {urn}")
            return response
        except Exception as e:
            self.logger.error(f"Failed to translate model: {str(e)}")
            return None

    def get_viewable_url(self, urn):
        """Get the URL for viewing the model"""
        try:
            manifest = self.forge.get_manifest(urn)
            if manifest['status'] == 'success':
                viewer_url = f"https://viewer.autodesk.com/viewer?urn={urn}"
                self.logger.info(f"Model ready for viewing: {viewer_url}")
                return viewer_url
            return None
        except Exception as e:
            self.logger.error(f"Failed to get viewable URL: {str(e)}")
            return None

    def create_viewer_html(self, viewer_url):
        """Create an HTML file for viewing the model"""
        try:
            html_content = f"""
            <!DOCTYPE html>
            <html>
            <head>
                <meta charset="UTF-8">
                <title>Eco-Vehicle Viewer</title>
                <link rel="stylesheet" href="https://developer.api.autodesk.com/modelderivative/v2/viewers/7.*/style.css">
                <script src="https://developer.api.autodesk.com/modelderivative/v2/viewers/7.*/viewer3D.js"></script>
                <style>
                    body {{ margin: 0; }}
                    #forgeViewer {{ width: 100%; height: 100vh; }}
                </style>
            </head>
            <body>
                <div id="forgeViewer"></div>
                <script>
                    var viewer;
                    var options = {{
                        env: 'AutodeskProduction',
                        api: 'derivativeV2',
                        getAccessToken: function(onTokenReady) {{
                            // Replace with your token generation logic
                            var token = '{self.forge.get_access_token()}';
                            var timeInSeconds = 3600;
                            onTokenReady(token, timeInSeconds);
                        }}
                    }};

                    Autodesk.Viewing.Initializer(options, function() {{
                        viewer = new Autodesk.Viewing.GuiViewer3D(document.getElementById('forgeViewer'));
                        viewer.start();
                        var documentId = '{viewer_url}';
                        Autodesk.Viewing.Document.load(documentId, onDocumentLoadSuccess, onDocumentLoadFailure);
                    }});

                    function onDocumentLoadSuccess(doc) {{
                        var viewables = doc.getRoot().getDefaultGeometry();
                        viewer.loadDocumentNode(doc, viewables).then(i => {{
                            // Viewer is ready
                        }});
                    }}

                    function onDocumentLoadFailure() {{
                        console.error('Failed to load model');
                    }}
                </script>
            </body>
            </html>
            """
            
            viewer_path = Path(__file__).resolve().parents[3] / "outputs/cad/viewer.html"
            with open(viewer_path, 'w') as f:
                f.write(html_content)
            
            self.logger.info(f"Created viewer HTML at: {viewer_path}")
            return str(viewer_path)
        except Exception as e:
            self.logger.error(f"Failed to create viewer HTML: {str(e)}")
            return None

def main():
    # Initialize the viewer
    viewer = ForgeViewer()
    
    # Set up environment variables first
    if not viewer.client_id or not viewer.client_secret:
        print("Please set FORGE_CLIENT_ID and FORGE_CLIENT_SECRET environment variables")
        return
    
    # Authenticate
    if not viewer.authenticate():
        return
    
    # Create bucket
    bucket_response = viewer.create_bucket()
    if not bucket_response:
        return
    
    # Upload model
    model_path = Path(__file__).resolve().parents[3] / "outputs/cad/eco_vehicle.dxf"
    upload_response = viewer.upload_model(str(model_path))
    if not upload_response:
        return
    
    # Translate model
    urn = upload_response['objectId']
    translation_response = viewer.translate_model(urn)
    if not translation_response:
        return
    
    # Get viewable URL
    viewer_url = viewer.get_viewable_url(urn)
    if not viewer_url:
        return
    
    # Create viewer HTML
    viewer_html = viewer.create_viewer_html(viewer_url)
    if viewer_html:
        print(f"Model viewer created at: {viewer_html}")
        print("Open this file in a web browser to view your model")

if __name__ == "__main__":
    main()
