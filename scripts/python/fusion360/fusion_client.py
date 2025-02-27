"""
Fusion 360 API Integration Client
"""
import os
from typing import Optional, Dict, Any
import adsk.core
import adsk.fusion
import traceback
from dotenv import load_dotenv

class FusionClient:
    def __init__(self):
        self.app: Optional[adsk.core.Application] = None
        self.ui: Optional[adsk.core.UserInterface] = None
        self.design: Optional[adsk.fusion.Design] = None
        
        # Load environment variables
        load_dotenv()
        
    def initialize(self) -> bool:
        """Initialize the Fusion 360 application connection"""
        try:
            self.app = adsk.core.Application.get()
            self.ui = self.app.userInterface
            self.design = self.app.activeProduct
            return True
        except:
            if self.ui:
                self.ui.messageBox(f'Failed to initialize:\n{traceback.format_exc()}')
            return False
    
    def create_new_design(self, name: str) -> Optional[adsk.fusion.Design]:
        """Create a new design document"""
        try:
            doc = self.app.documents.add(adsk.core.DocumentTypes.FusionDesignDocumentType)
            design = self.app.activeProduct
            design.designType = adsk.fusion.DesignTypes.ParametricDesignType
            return design
        except:
            if self.ui:
                self.ui.messageBox(f'Failed to create design:\n{traceback.format_exc()}')
            return None
    
    def save_design(self, filepath: str) -> bool:
        """Save the current design"""
        try:
            doc = self.app.activeDocument
            doc.saveAs(filepath, "", "")
            return True
        except:
            if self.ui:
                self.ui.messageBox(f'Failed to save design:\n{traceback.format_exc()}')
            return False
    
    def export_design(self, filepath: str, file_type: str) -> bool:
        """Export the current design to specified format"""
        try:
            export_mgr = self.design.exportManager
            export_options = None
            
            if file_type.lower() == 'stl':
                export_options = export_mgr.createSTLExportOptions(
                    self.design.rootComponent)
            elif file_type.lower() == 'step':
                export_options = export_mgr.createSTEPExportOptions(
                    self.design.rootComponent)
            
            if export_options:
                export_options.filename = filepath
                return export_mgr.execute(export_options)
            return False
        except:
            if self.ui:
                self.ui.messageBox(f'Failed to export design:\n{traceback.format_exc()}')
            return False
