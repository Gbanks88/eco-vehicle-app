import os
import json
from typing import Dict, Any, Optional
from pathlib import Path
import pymongo
from ibmcloudant import CloudantV1
from ibm_cloud_sdk_core.authenticators import IAMAuthenticator
from ibm_db import connect
import ibm_boto3
from pymongo import MongoClient
from dotenv import load_dotenv

class DatabaseConnectionManager:
    def __init__(self, config_path: str = None):
        load_dotenv()
        self.config = self._load_config(config_path)
        self.connections = {}
        
    def _load_config(self, config_path: Optional[str] = None) -> Dict[str, Any]:
        if not config_path:
            config_path = os.path.join(os.path.dirname(__file__), '..', 'config', 'database.json')
        
        with open(config_path, 'r') as f:
            return json.load(f)
    
    def get_studio3t_connection(self) -> MongoClient:
        """Get MongoDB connection via Studio 3T"""
        if 'studio3t' not in self.connections:
            config = self.config['mongodb']['studio3t']
            client = MongoClient(
                config['uri'],
                **config['options']
            )
            self.connections['studio3t'] = client
        return self.connections['studio3t']
    
    def get_ibm_db2_connection(self) -> Any:
        """Get IBM Db2 connection"""
        if 'db2' not in self.connections:
            creds = self.config['ibm_cloud']['credentials']
            db_config = self.config['ibm_cloud']['services']['db2']
            
            dsn = (
                f"DATABASE={db_config['database']};"
                f"HOSTNAME={creds['url']};"
                f"PORT=50000;PROTOCOL=TCPIP;"
                f"UID={os.getenv('IBM_DB2_USER')};"
                f"PWD={os.getenv('IBM_DB2_PASSWORD')};"
            )
            
            conn = connect(dsn, "", "")
            self.connections['db2'] = conn
        return self.connections['db2']
    
    def get_cloudant_client(self) -> CloudantV1:
        """Get IBM Cloudant client"""
        if 'cloudant' not in self.connections:
            creds = self.config['ibm_cloud']['credentials']
            authenticator = IAMAuthenticator(creds['apikey'])
            client = CloudantV1(authenticator=authenticator)
            client.set_service_url(creds['url'])
            self.connections['cloudant'] = client
        return self.connections['cloudant']
    
    def get_object_storage_client(self) -> 'ibm_boto3.client':
        """Get IBM Cloud Object Storage client"""
        if 'cos' not in self.connections:
            creds = self.config['ibm_cloud']['credentials']
            cos = ibm_boto3.client(
                's3',
                ibm_api_key_id=creds['apikey'],
                ibm_service_instance_id=creds['instance_id'],
                ibm_auth_endpoint="https://iam.cloud.ibm.com/identity/token",
                config=ibm_boto3.Config(signature_version='oauth'),
                endpoint_url=f"https://s3.{self.config['ibm_cloud']['services']['object_storage']['region']}.cloud-object-storage.appdomain.cloud"
            )
            self.connections['cos'] = cos
        return self.connections['cos']
    
    def close_all_connections(self):
        """Close all active database connections"""
        for conn_type, conn in self.connections.items():
            try:
                if conn_type == 'studio3t':
                    conn.close()
                elif conn_type == 'db2':
                    conn.close()
                elif conn_type == 'cloudant':
                    # Cloudant uses HTTP, no need to close
                    pass
                elif conn_type == 'cos':
                    # COS uses HTTP, no need to close
                    pass
            except Exception as e:
                print(f"Error closing {conn_type} connection: {e}")
        self.connections = {}
