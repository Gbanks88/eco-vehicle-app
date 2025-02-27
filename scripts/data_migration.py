import os
import json
import logging
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, List
import pandas as pd
from tqdm import tqdm
from concurrent.futures import ThreadPoolExecutor
from database.connection_manager import DatabaseConnectionManager

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class DataMigrationTool:
    def __init__(self):
        self.db_manager = DatabaseConnectionManager()
        self.mongo = self.db_manager.get_studio3t_connection()
        self.db2_conn = self.db_manager.get_ibm_db2_connection()
        self.cloudant = self.db_manager.get_cloudant_client()
        self.cos = self.db_manager.get_object_storage_client()
        
    def export_to_csv(self, collection_name: str, query: Dict = None, output_dir: str = 'exports'):
        """Export MongoDB collection to CSV"""
        logger.info(f"Exporting {collection_name} to CSV...")
        
        # Create output directory if it doesn't exist
        Path(output_dir).mkdir(parents=True, exist_ok=True)
        
        # Get data from MongoDB
        data = list(self.mongo.cg4f_analytics[collection_name].find(query or {}))
        
        if not data:
            logger.warning(f"No data found in {collection_name}")
            return
        
        # Convert to DataFrame and export
        df = pd.DataFrame(data)
        output_file = f"{output_dir}/{collection_name}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
        df.to_csv(output_file, index=False)
        logger.info(f"Exported to {output_file}")
        
        # Upload to Cloud Object Storage
        with open(output_file, 'rb') as f:
            self.cos.put_object(
                Bucket=os.getenv('COS_BUCKET'),
                Key=f"exports/{os.path.basename(output_file)}",
                Body=f
            )
        logger.info(f"Uploaded to Cloud Object Storage")
    
    def migrate_to_db2(self, collection_name: str, batch_size: int = 1000):
        """Migrate data from MongoDB to IBM DB2"""
        logger.info(f"Migrating {collection_name} to DB2...")
        
        # Get total count for progress bar
        total = self.mongo.cg4f_analytics[collection_name].count_documents({})
        
        for i in tqdm(range(0, total, batch_size)):
            batch = list(self.mongo.cg4f_analytics[collection_name]
                        .find({})
                        .skip(i)
                        .limit(batch_size))
            
            if not batch:
                continue
            
            # Convert to DataFrame for easier handling
            df = pd.DataFrame(batch)
            
            # Prepare SQL statement
            columns = ', '.join(df.columns)
            placeholders = ', '.join(['?'] * len(df.columns))
            
            # Insert batch
            stmt = f"INSERT INTO analytics.{collection_name} ({columns}) VALUES ({placeholders})"
            
            for _, row in df.iterrows():
                self.db2_conn.execute(stmt, tuple(row))
            
        logger.info(f"Migration completed for {collection_name}")
    
    def sync_databases(self):
        """Synchronize data between MongoDB and IBM DB2"""
        logger.info("Starting database synchronization...")
        
        collections = ['vehicle_metrics', 'ml_predictions', 'system_optimization']
        
        for collection in collections:
            # Get latest timestamp from DB2
            query = f"SELECT MAX(timestamp) as max_ts FROM analytics.{collection}"
            result = self.db2_conn.execute(query).fetchone()
            last_sync = result[0] if result[0] else datetime.min
            
            # Get new records from MongoDB
            new_records = list(self.mongo.cg4f_analytics[collection].find({
                'timestamp': {'$gt': last_sync}
            }))
            
            if new_records:
                logger.info(f"Found {len(new_records)} new records in {collection}")
                self.migrate_to_db2(collection)
            else:
                logger.info(f"No new records found in {collection}")
    
    def backup_databases(self, backup_dir: str = 'backups'):
        """Create backups of all databases"""
        logger.info("Starting database backup...")
        
        # Create backup directory
        backup_path = Path(backup_dir) / datetime.now().strftime('%Y%m%d_%H%M%S')
        backup_path.mkdir(parents=True, exist_ok=True)
        
        # Backup MongoDB
        logger.info("Backing up MongoDB...")
        collections = ['vehicle_metrics', 'ml_predictions', 'system_optimization']
        
        for collection in collections:
            self.export_to_csv(collection, output_dir=str(backup_path))
        
        # Backup DB2
        logger.info("Backing up DB2...")
        tables = ['vehicle_metrics', 'system_optimization']
        
        for table in tables:
            query = f"SELECT * FROM analytics.{table}"
            df = pd.read_sql(query, self.db2_conn)
            df.to_csv(backup_path / f"db2_{table}.csv", index=False)
        
        # Backup Cloudant
        logger.info("Backing up Cloudant...")
        databases = ['cg4f_realtime']
        
        for db in databases:
            docs = self.cloudant.post_all_docs(
                db=db,
                include_docs=True
            ).get_result()
            
            with open(backup_path / f"cloudant_{db}.json", 'w') as f:
                json.dump(docs, f, indent=2)
        
        # Upload backup to Cloud Object Storage
        logger.info("Uploading backup to Cloud Object Storage...")
        for file in backup_path.glob('*'):
            with open(file, 'rb') as f:
                self.cos.put_object(
                    Bucket=os.getenv('COS_BUCKET'),
                    Key=f"backups/{file.parent.name}/{file.name}",
                    Body=f
                )
        
        logger.info(f"Backup completed and stored in {backup_path}")

def main():
    """Run data migration and management tasks"""
    tool = DataMigrationTool()
    
    # Parse command line arguments
    import argparse
    parser = argparse.ArgumentParser(description='Data Migration and Management Tool')
    parser.add_argument('--export', help='Export collection to CSV')
    parser.add_argument('--migrate', help='Migrate collection to DB2')
    parser.add_argument('--sync', action='store_true', help='Synchronize databases')
    parser.add_argument('--backup', action='store_true', help='Create database backups')
    
    args = parser.parse_args()
    
    try:
        if args.export:
            tool.export_to_csv(args.export)
        elif args.migrate:
            tool.migrate_to_db2(args.migrate)
        elif args.sync:
            tool.sync_databases()
        elif args.backup:
            tool.backup_databases()
        else:
            parser.print_help()
    except Exception as e:
        logger.error(f"Error: {e}")
        raise

if __name__ == '__main__':
    main()
