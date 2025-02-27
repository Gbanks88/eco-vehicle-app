from typing import Dict, List, Any, Optional
from datetime import datetime
import pandas as pd
from .connection_manager import DatabaseConnectionManager

class AnalyticsDAO:
    def __init__(self, db_manager: DatabaseConnectionManager):
        self.db_manager = db_manager
        self.mongo_client = db_manager.get_studio3t_connection()
        self.db2_conn = db_manager.get_ibm_db2_connection()
        self.cloudant = db_manager.get_cloudant_client()
        self.cos = db_manager.get_object_storage_client()
        
    def store_vehicle_metrics(self, metrics: Dict[str, Any]):
        """Store vehicle metrics in both MongoDB and IBM DB2"""
        # Store in MongoDB via Studio 3T
        mongo_db = self.mongo_client.cg4f_analytics
        mongo_db.vehicle_metrics.insert_one({
            **metrics,
            'timestamp': datetime.utcnow()
        })
        
        # Store in IBM DB2
        columns = ', '.join(metrics.keys())
        values = ', '.join([f"'{v}'" if isinstance(v, str) else str(v) for v in metrics.values()])
        query = f"INSERT INTO analytics.vehicle_metrics ({columns}) VALUES ({values})"
        self.db2_conn.execute(query)
    
    def get_vehicle_metrics(self, start_time: datetime, end_time: datetime) -> pd.DataFrame:
        """Get vehicle metrics from both sources and merge them"""
        # Get from MongoDB
        mongo_db = self.mongo_client.cg4f_analytics
        mongo_metrics = list(mongo_db.vehicle_metrics.find({
            'timestamp': {
                '$gte': start_time,
                '$lte': end_time
            }
        }))
        
        # Get from IBM DB2
        query = f"""
            SELECT * FROM analytics.vehicle_metrics 
            WHERE timestamp BETWEEN '{start_time}' AND '{end_time}'
        """
        db2_metrics = pd.read_sql(query, self.db2_conn)
        
        # Merge and deduplicate
        mongo_df = pd.DataFrame(mongo_metrics)
        merged_df = pd.concat([mongo_df, db2_metrics]).drop_duplicates()
        return merged_df
    
    def store_ml_prediction(self, prediction: Dict[str, Any]):
        """Store ML prediction results"""
        # Store in MongoDB
        mongo_db = self.mongo_client.cg4f_analytics
        mongo_db.ml_predictions.insert_one({
            **prediction,
            'timestamp': datetime.utcnow()
        })
        
        # Store in IBM Cloudant for real-time access
        self.cloudant.post_document(
            db='cg4f_realtime',
            document=prediction
        ).get_result()
    
    def get_ml_predictions(self, vehicle_id: str, limit: int = 100) -> List[Dict[str, Any]]:
        """Get ML predictions for a specific vehicle"""
        mongo_db = self.mongo_client.cg4f_analytics
        return list(mongo_db.ml_predictions.find(
            {'vehicle_id': vehicle_id}
        ).sort('timestamp', -1).limit(limit))
    
    def store_optimization_result(self, result: Dict[str, Any]):
        """Store system optimization results"""
        # Store in MongoDB
        mongo_db = self.mongo_client.cg4f_analytics
        mongo_db.system_optimization.insert_one({
            **result,
            'timestamp': datetime.utcnow()
        })
        
        # Store in IBM DB2
        columns = ', '.join(result.keys())
        values = ', '.join([f"'{v}'" if isinstance(v, str) else str(v) for v in result.values()])
        query = f"INSERT INTO analytics.system_optimization ({columns}) VALUES ({values})"
        self.db2_conn.execute(query)
    
    def store_large_dataset(self, data: bytes, filename: str):
        """Store large datasets in IBM Cloud Object Storage"""
        bucket = self.config['ibm_cloud']['services']['object_storage']['bucket']
        self.cos.put_object(
            Bucket=bucket,
            Key=filename,
            Body=data
        )
    
    def get_large_dataset(self, filename: str) -> bytes:
        """Retrieve large datasets from IBM Cloud Object Storage"""
        bucket = self.config['ibm_cloud']['services']['object_storage']['bucket']
        response = self.cos.get_object(
            Bucket=bucket,
            Key=filename
        )
        return response['Body'].read()
    
    def store_system_event(self, event: Dict[str, Any]):
        """Store system events in Cloudant"""
        self.cloudant.post_document(
            db='cg4f_realtime',
            document={
                **event,
                'timestamp': datetime.utcnow().isoformat()
            }
        ).get_result()
    
    def get_system_events(self, start_time: datetime, end_time: datetime) -> List[Dict[str, Any]]:
        """Get system events from Cloudant"""
        selector = {
            'timestamp': {
                '$gte': start_time.isoformat(),
                '$lte': end_time.isoformat()
            }
        }
        result = self.cloudant.post_find(
            db='cg4f_realtime',
            selector=selector
        ).get_result()
        return result['docs']
