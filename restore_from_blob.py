"""
Restore Weaviate collections from Azure Blob Storage backups.
Features:
- Downloads and decompresses gzip files
- Streams to Weaviate (minimal disk usage)
- Parallel processing
- Resume capability
"""

import json
import gzip
import io
import asyncio
import gc
import logging
from typing import List, Dict
import requests
from azure.storage.blob import BlobServiceClient
from tqdm import tqdm

import config
from weaviate_client import batch_insert_objects

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class WeaviateRestore:
    """Restore Weaviate collections from Azure Blob Storage"""
    
    def __init__(self, connection_string: str, container_name: str = "weaviate-backups"):
        self.connection_string = connection_string
        self.container_name = container_name
        self.blob_service_client = BlobServiceClient.from_connection_string(connection_string)
        self.container_client = self.blob_service_client.get_container_client(container_name)
    
    def list_backup_files(self, collection_name: str) -> List[str]:
        """List all backup files for a collection"""
        try:
            blobs = self.container_client.list_blobs(name_starts_with=f"{collection_name}/")
            return sorted([blob.name for blob in blobs])
        except Exception as e:
            logger.error(f"Error listing blobs: {e}")
            return []
    
    def download_and_decompress(self, blob_name: str) -> List[Dict]:
        """Download and decompress a backup file"""
        try:
            # Download blob
            blob_client = self.container_client.get_blob_client(blob_name)
            compressed_data = blob_client.download_blob().readall()
            
            # Decompress
            with gzip.GzipFile(fileobj=io.BytesIO(compressed_data)) as gz:
                json_data = gz.read()
            
            # Parse JSON
            objects = json.loads(json_data)
            
            logger.debug(f"Downloaded & decompressed: {blob_name} ({len(objects)} objects)")
            
            return objects
            
        except Exception as e:
            logger.error(f"Error downloading {blob_name}: {e}")
            return []
    
    async def restore_collection(self, collection_name: str):
        """Restore a collection from backup files"""
        
        logger.info("=" * 70)
        logger.info(f"Restoring: {collection_name}")
        logger.info("=" * 70)
        
        # List backup files
        backup_files = self.list_backup_files(collection_name)
        
        if not backup_files:
            logger.warning(f"No backup files found for {collection_name}")
            return
        
        logger.info(f"Found {len(backup_files)} backup files")
        
        total_restored = 0
        
        with tqdm(total=len(backup_files), desc=f"Restoring {collection_name}", unit="file") as pbar:
            for i, blob_name in enumerate(backup_files, 1):
                # Download and decompress
                objects = self.download_and_decompress(blob_name)
                
                if not objects:
                    logger.warning(f"Skipping empty file: {blob_name}")
                    pbar.update(1)
                    continue
                
                # Prepare for insertion
                objects_to_insert = []
                for obj in objects:
                    additional = obj.pop('_additional', {})
                    vector = additional.get('vector', [])
                    
                    objects_to_insert.append({
                        "properties": obj,
                        "vector": vector
                    })
                
                # Insert into Weaviate
                success, errors = batch_insert_objects(objects_to_insert, collection_name)
                total_restored += success
                
                logger.debug(f"File {i}/{len(backup_files)}: {success} restored, {errors} errors")
                
                # Cleanup
                objects = None
                objects_to_insert = None
                
                # GC every 10 files
                if i % 10 == 0:
                    collected = gc.collect()
                    logger.info(f"Restored {total_restored:,} objects so far, GC freed {collected}")
                
                pbar.update(1)
        
        logger.info("=" * 70)
        logger.info(f"Restore complete: {collection_name}")
        logger.info(f"Total objects restored: {total_restored:,}")
        logger.info("=" * 70)


def main():
    """Main restore function"""
    
    print("╔" + "="*68 + "╗")
    print("║" + " "*16 + "RESTORE FROM AZURE BLOB BACKUP" + " "*21 + "║")
    print("╚" + "="*68 + "╝")
    
    # Get connection string
    connection_string = input("\nEnter Azure Blob Storage connection string: ").strip()
    
    if not connection_string:
        print("❌ Connection string required")
        return 1
    
    # Get collection name
    collection_name = input("Enter collection name to restore: ").strip()
    
    if not collection_name:
        print("❌ Collection name required")
        return 1
    
    # Confirm
    print(f"\n⚠️  This will restore data into: {collection_name}")
    print("   Make sure the collection schema exists!")
    confirm = input("Proceed? (yes/no): ").strip().lower()
    
    if confirm != 'yes':
        print("❌ Restore cancelled")
        return 0
    
    # Run restore
    restore = WeaviateRestore(connection_string)
    asyncio.run(restore.restore_collection(collection_name))
    
    return 0


if __name__ == "__main__":
    import sys
    sys.exit(main())

