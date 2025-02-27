import os
import time
import logging
import schedule
from datetime import datetime, timedelta
from typing import Dict, Any, List
import pandas as pd
from database.connection_manager import DatabaseConnectionManager
from concurrent.futures import ThreadPoolExecutor

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class DataSyncService:
    def __init__(self):
        self.db_manager = DatabaseConnectionManager()
        self.mongo = self.db_manager.get_studio3t_connection()
        self.db2_conn = self.db_manager.get_ibm_db2_connection()
        self.cloudant = self.db_manager.get_cloudant_client()
        self.cos = self.db_manager.get_object_storage_client()
        self.sync_status = {
            'last_sync': None,
            'status': 'idle',
            'errors': []
        }
    
    def sync_vehicle_metrics(self):
        """Synchronize vehicle metrics between MongoDB and DB2"""
        try:
            logger.info("Syncing vehicle metrics...")
            self.sync_status['status'] = 'syncing_metrics'
            
            # Get latest timestamp from DB2
            query = "SELECT MAX(timestamp) as max_ts FROM analytics.vehicle_metrics"
            result = self.db2_conn.execute(query).fetchone()
            last_sync = result[0] if result[0] else datetime.min
            
            # Get new records from MongoDB
            new_records = list(self.mongo.cg4f_analytics.vehicle_metrics.find({
                'timestamp': {'$gt': last_sync}
            }))
            
            if new_records:
                df = pd.DataFrame(new_records)
                
                # Insert into DB2
                for _, row in df.iterrows():
                    columns = ', '.join(row.index)
                    values = ', '.join(['?'] * len(row))
                    stmt = f"INSERT INTO analytics.vehicle_metrics ({columns}) VALUES ({values})"
                    self.db2_conn.execute(stmt, tuple(row))
                
                logger.info(f"Synced {len(new_records)} vehicle metrics")
            
            self.sync_status['last_sync'] = datetime.now()
            self.sync_status['status'] = 'idle'
            
        except Exception as e:
            logger.error(f"Error syncing vehicle metrics: {e}")
            self.sync_status['errors'].append({
                'timestamp': datetime.now(),
                'component': 'vehicle_metrics',
                'error': str(e)
            })
    
    def sync_ml_predictions(self):
        """Synchronize ML predictions between MongoDB and Cloudant"""
        try:
            logger.info("Syncing ML predictions...")
            self.sync_status['status'] = 'syncing_predictions'
            
            # Get latest predictions from MongoDB
            cutoff = datetime.now() - timedelta(hours=1)
            predictions = list(self.mongo.cg4f_analytics.ml_predictions.find({
                'timestamp': {'$gt': cutoff}
            }))
            
            if predictions:
                # Batch upload to Cloudant
                self.cloudant.post_bulk_docs(
                    db='cg4f_realtime',
                    bulk_docs={'docs': predictions}
                ).get_result()
                
                logger.info(f"Synced {len(predictions)} ML predictions")
            
            self.sync_status['last_sync'] = datetime.now()
            self.sync_status['status'] = 'idle'
            
        except Exception as e:
            logger.error(f"Error syncing ML predictions: {e}")
            self.sync_status['errors'].append({
                'timestamp': datetime.now(),
                'component': 'ml_predictions',
                'error': str(e)
            })
    
    def sync_system_events(self):
        """Synchronize system events between Cloudant and MongoDB"""
        try:
            logger.info("Syncing system events...")
            self.sync_status['status'] = 'syncing_events'
            
            # Get events from Cloudant
            result = self.cloudant.post_all_docs(
                db='cg4f_realtime',
                include_docs=True
            ).get_result()
            
            events = [doc['doc'] for doc in result['rows']]
            
            if events:
                # Insert into MongoDB
                self.mongo.cg4f_analytics.system_events.insert_many(events)
                
                logger.info(f"Synced {len(events)} system events")
            
            self.sync_status['last_sync'] = datetime.now()
            self.sync_status['status'] = 'idle'
            
        except Exception as e:
            logger.error(f"Error syncing system events: {e}")
            self.sync_status['errors'].append({
                'timestamp': datetime.now(),
                'component': 'system_events',
                'error': str(e)
            })
    
    def archive_old_data(self):
        """Archive old data to Cloud Object Storage"""
        try:
            logger.info("Archiving old data...")
            self.sync_status['status'] = 'archiving'
            
            # Archive data older than 30 days
            cutoff = datetime.now() - timedelta(days=30)
            
            # Archive from MongoDB
            old_metrics = list(self.mongo.cg4f_analytics.vehicle_metrics.find({
                'timestamp': {'$lt': cutoff}
            }))
            
            if old_metrics:
                # Convert to CSV and upload to COS
                df = pd.DataFrame(old_metrics)
                csv_data = df.to_csv(index=False).encode()
                
                filename = f"archive/vehicle_metrics_{datetime.now().strftime('%Y%m%d')}.csv"
                self.cos.put_object(
                    Bucket=os.getenv('COS_BUCKET'),
                    Key=filename,
                    Body=csv_data
                )
                
                # Delete archived data
                self.mongo.cg4f_analytics.vehicle_metrics.delete_many({
                    'timestamp': {'$lt': cutoff}
                })
                
                logger.info(f"Archived {len(old_metrics)} records")
            
            self.sync_status['last_sync'] = datetime.now()
            self.sync_status['status'] = 'idle'
            
        except Exception as e:
            logger.error(f"Error archiving data: {e}")
            self.sync_status['errors'].append({
                'timestamp': datetime.now(),
                'component': 'archiving',
                'error': str(e)
            })
    
    def get_sync_status(self) -> Dict[str, Any]:
        """Get current sync status"""
        return {
            'last_sync': self.sync_status['last_sync'],
            'status': self.sync_status['status'],
            'errors': self.sync_status['errors'][-10:],  # Last 10 errors
            'metrics': {
                'vehicle_metrics': self.mongo.cg4f_analytics.vehicle_metrics.count_documents({}),
                'ml_predictions': self.mongo.cg4f_analytics.ml_predictions.count_documents({}),
                'system_events': self.mongo.cg4f_analytics.system_events.count_documents({})
            }
        }
    
    def start_sync_scheduler(self):
        """Start the sync scheduler"""
        logger.info("Starting sync scheduler...")
        
        # Schedule sync jobs
        schedule.every(5).minutes.do(self.sync_vehicle_metrics)
        schedule.every(10).minutes.do(self.sync_ml_predictions)
        schedule.every(15).minutes.do(self.sync_system_events)
        schedule.every().day.at("00:00").do(self.archive_old_data)
        
        while True:
            try:
                schedule.run_pending()
                time.sleep(60)
            except Exception as e:
                logger.error(f"Scheduler error: {e}")
                time.sleep(300)  # Wait 5 minutes before retrying

def main():
    """Run the data sync service"""
    sync_service = DataSyncService()
    
    # Run initial sync
    with ThreadPoolExecutor(max_workers=3) as executor:
        executor.submit(sync_service.sync_vehicle_metrics)
        executor.submit(sync_service.sync_ml_predictions)
        executor.submit(sync_service.sync_system_events)
    
    # Start scheduler
    sync_service.start_sync_scheduler()

if __name__ == '__main__':
    main()
