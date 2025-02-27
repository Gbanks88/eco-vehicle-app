import os
from pathlib import Path
import json
from typing import Dict, Any
from ibm_db import exec_immediate
from pymongo import MongoClient
from ibmcloudant import CloudantV1
from ibm_cloud_sdk_core.authenticators import IAMAuthenticator
import ibm_boto3

def load_config() -> Dict[str, Any]:
    config_path = Path(__file__).parent.parent / 'src' / 'config' / 'database.json'
    with open(config_path, 'r') as f:
        return json.load(f)

def init_mongodb():
    """Initialize MongoDB collections via Studio 3T"""
    print("Initializing MongoDB collections...")
    config = load_config()['mongodb']['studio3t']
    
    client = MongoClient(config['uri'])
    db = client[config['database']]
    
    # Create collections with validators
    db.create_collection('vehicle_metrics', validator={
        '$jsonSchema': {
            'bsonType': 'object',
            'required': ['vehicle_id', 'timestamp', 'metrics'],
            'properties': {
                'vehicle_id': {'bsonType': 'string'},
                'timestamp': {'bsonType': 'date'},
                'metrics': {'bsonType': 'object'}
            }
        }
    })
    
    db.create_collection('ml_predictions', validator={
        '$jsonSchema': {
            'bsonType': 'object',
            'required': ['vehicle_id', 'timestamp', 'model_type', 'predictions'],
            'properties': {
                'vehicle_id': {'bsonType': 'string'},
                'timestamp': {'bsonType': 'date'},
                'model_type': {'bsonType': 'string'},
                'predictions': {'bsonType': 'object'}
            }
        }
    })
    
    # Create indexes
    db.vehicle_metrics.create_index([('vehicle_id', 1), ('timestamp', -1)])
    db.ml_predictions.create_index([('vehicle_id', 1), ('timestamp', -1)])
    
    print("MongoDB collections initialized successfully")

def init_db2():
    """Initialize IBM DB2 tables"""
    print("Initializing IBM DB2 tables...")
    config = load_config()['ibm_cloud']
    
    # Connect to DB2
    dsn = (
        f"DATABASE={config['services']['db2']['database']};"
        f"HOSTNAME={config['credentials']['url']};"
        f"PORT=50000;PROTOCOL=TCPIP;"
        f"UID={os.getenv('IBM_DB2_USER')};"
        f"PWD={os.getenv('IBM_DB2_PASSWORD')};"
    )
    
    conn = connect(dsn, "", "")
    
    # Create schema if not exists
    exec_immediate(conn, "CREATE SCHEMA IF NOT EXISTS analytics")
    
    # Create tables
    exec_immediate(conn, """
        CREATE TABLE IF NOT EXISTS analytics.vehicle_metrics (
            id INTEGER GENERATED ALWAYS AS IDENTITY,
            vehicle_id VARCHAR(50) NOT NULL,
            timestamp TIMESTAMP NOT NULL,
            speed DOUBLE,
            battery_level DOUBLE,
            temperature DOUBLE,
            pressure DOUBLE,
            efficiency DOUBLE,
            PRIMARY KEY (id)
        )
    """)
    
    exec_immediate(conn, """
        CREATE TABLE IF NOT EXISTS analytics.system_optimization (
            id INTEGER GENERATED ALWAYS AS IDENTITY,
            timestamp TIMESTAMP NOT NULL,
            optimization_type VARCHAR(50) NOT NULL,
            parameters CLOB,
            results CLOB,
            efficiency_gain DOUBLE,
            PRIMARY KEY (id)
        )
    """)
    
    # Create indexes
    exec_immediate(conn, """
        CREATE INDEX IF NOT EXISTS idx_vehicle_metrics 
        ON analytics.vehicle_metrics(vehicle_id, timestamp)
    """)
    
    print("IBM DB2 tables initialized successfully")

def init_cloudant():
    """Initialize IBM Cloudant databases"""
    print("Initializing IBM Cloudant databases...")
    config = load_config()['ibm_cloud']
    
    authenticator = IAMAuthenticator(config['credentials']['apikey'])
    client = CloudantV1(authenticator=authenticator)
    client.set_service_url(config['credentials']['url'])
    
    # Create databases
    try:
        client.put_database(db='cg4f_realtime').get_result()
    except Exception as e:
        if 'file_exists' not in str(e):
            raise
    
    # Create design documents for views
    events_design = {
        '_id': '_design/events',
        'views': {
            'by_timestamp': {
                'map': '''
                function(doc) {
                    if (doc.timestamp) {
                        emit(doc.timestamp, doc);
                    }
                }
                '''
            }
        }
    }
    
    try:
        client.put_design_document(
            db='cg4f_realtime',
            design_document='events',
            design_document_body=events_design
        ).get_result()
    except Exception as e:
        if 'conflict' not in str(e):
            raise
    
    print("IBM Cloudant databases initialized successfully")

def init_object_storage():
    """Initialize IBM Cloud Object Storage buckets"""
    print("Initializing IBM Cloud Object Storage...")
    config = load_config()['ibm_cloud']
    
    cos = ibm_boto3.client(
        's3',
        ibm_api_key_id=config['credentials']['apikey'],
        ibm_service_instance_id=config['credentials']['instance_id'],
        ibm_auth_endpoint="https://iam.cloud.ibm.com/identity/token",
        config=ibm_boto3.Config(signature_version='oauth'),
        endpoint_url=f"https://s3.{config['services']['object_storage']['region']}.cloud-object-storage.appdomain.cloud"
    )
    
    bucket = config['services']['object_storage']['bucket']
    
    try:
        cos.create_bucket(
            Bucket=bucket,
            CreateBucketConfiguration={
                'LocationConstraint': f"{config['services']['object_storage']['region']}-smart"
            }
        )
    except Exception as e:
        if 'BucketAlreadyExists' not in str(e):
            raise
    
    print("IBM Cloud Object Storage initialized successfully")

def main():
    """Initialize all databases"""
    try:
        init_mongodb()
        init_db2()
        init_cloudant()
        init_object_storage()
        print("\nAll databases initialized successfully!")
    except Exception as e:
        print(f"\nError initializing databases: {e}")
        raise

if __name__ == '__main__':
    main()
