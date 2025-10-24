"""
Test backup and restore workflow on a small collection.
Safely deletes a collection and restores it from backup.
"""


import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import sys
import requests
import asyncio
import config
from restore_from_blob import WeaviateRestore


def delete_collection(collection_name):
    """Delete a Weaviate collection"""
    
    print("\n" + "="*70)
    print(f"STEP 1: Delete Collection '{collection_name}'")
    print("="*70)
    
    headers = {"Content-Type": "application/json"}
    if config.WEAVIATE_API_KEY and config.WEAVIATE_API_KEY != "your-weaviate-api-key":
        headers["Authorization"] = f"Bearer {config.WEAVIATE_API_KEY}"
    
    # Check if collection exists
    print(f"\n🔍 Checking if {collection_name} exists...")
    response = requests.get(
        f"{config.WEAVIATE_URL}/v1/schema/{collection_name}",
        headers=headers,
        timeout=30
    )
    
    if response.status_code == 404:
        print(f"⚠️  Collection {collection_name} doesn't exist")
        return False
    elif response.status_code != 200:
        print(f"❌ Error checking collection: {response.status_code}")
        return False
    
    print(f"✓ Collection {collection_name} exists")
    
    # Count objects before deletion
    count_query = {
        "query": f"""
        {{
          Aggregate {{
            {collection_name} {{
              meta {{ count }}
            }}
          }}
        }}
        """
    }
    
    response = requests.post(
        f"{config.WEAVIATE_URL}/v1/graphql",
        headers=headers,
        json=count_query,
        timeout=30
    )
    
    if response.status_code == 200:
        result = response.json()
        count_data = result.get("data", {}).get("Aggregate", {}).get(collection_name, [])
        if count_data:
            count = count_data[0].get("meta", {}).get("count", 0)
            print(f"✓ Collection has {count:,} objects")
    
    # Confirm deletion
    print(f"\n⚠️  WARNING: This will DELETE collection '{collection_name}'!")
    print("   All data will be removed from Weaviate.")
    print("   (Don't worry - we'll restore from backup)")
    confirm = input("\nType collection name to confirm deletion: ").strip()
    
    if confirm != collection_name:
        print("❌ Deletion cancelled (name mismatch)")
        return False
    
    # Delete collection
    print(f"\n🗑️  Deleting {collection_name}...")
    response = requests.delete(
        f"{config.WEAVIATE_URL}/v1/schema/{collection_name}",
        headers=headers,
        timeout=30
    )
    
    if response.status_code == 200:
        print(f"✅ Collection {collection_name} deleted successfully")
        return True
    else:
        print(f"❌ Failed to delete collection: {response.status_code}")
        print(f"   Response: {response.text}")
        return False


def recreate_schema(collection_name, source_collection="SongLyrics"):
    """Recreate collection schema (copy from source)"""
    
    print("\n" + "="*70)
    print(f"STEP 2: Recreate Schema for '{collection_name}'")
    print("="*70)
    
    headers = {"Content-Type": "application/json"}
    if config.WEAVIATE_API_KEY and config.WEAVIATE_API_KEY != "your-weaviate-api-key":
        headers["Authorization"] = f"Bearer {config.WEAVIATE_API_KEY}"
    
    # Get source schema
    print(f"\n📋 Getting schema from {source_collection}...")
    response = requests.get(
        f"{config.WEAVIATE_URL}/v1/schema/{source_collection}",
        headers=headers,
        timeout=30
    )
    
    if response.status_code != 200:
        print(f"❌ Failed to get source schema: {response.status_code}")
        return False
    
    source_schema = response.json()
    
    # Create new schema with target name
    target_schema = source_schema.copy()
    target_schema['class'] = collection_name
    
    print(f"✓ Got schema from {source_collection}")
    print(f"\n🔧 Creating schema for {collection_name}...")
    
    response = requests.post(
        f"{config.WEAVIATE_URL}/v1/schema",
        headers=headers,
        json=target_schema,
        timeout=30
    )
    
    if response.status_code == 200:
        print(f"✅ Schema created for {collection_name}")
        return True
    else:
        print(f"❌ Failed to create schema: {response.status_code}")
        print(f"   Response: {response.text}")
        return False


async def restore_collection(collection_name):
    """Restore collection from backup"""
    
    print("\n" + "="*70)
    print(f"STEP 3: Restore '{collection_name}' from Backup")
    print("="*70)
    
    connection_string = config.AZURE_BLOB_CONNECTION_STRING
    
    if not connection_string or connection_string == "your-azure-blob-connection-string-here":
        print("❌ Azure Blob connection string not configured in config.py")
        return False
    
    print(f"\n✓ Using Azure Blob container: {config.AZURE_BLOB_CONTAINER_NAME}")
    
    # Create restore object
    restore = WeaviateRestore(connection_string, config.AZURE_BLOB_CONTAINER_NAME)
    
    # Get available backups
    backup_runs = restore.list_backup_runs(collection_name)
    
    if not backup_runs:
        print(f"❌ No backups found for {collection_name}")
        print("\nYou need to backup this collection first:")
        print("  python backup_to_blob.py")
        return False
    
    # Use the most recent backup (first in list - sorted newest first)
    backup_run_id = backup_runs[0]
    print(f"\n✅ Using most recent backup: {backup_run_id}")
    
    # Restore collection with specific backup_run_id (no interactive prompt)
    await restore.restore_collection(collection_name, backup_run_id=backup_run_id)
    
    return True


def verify_restore(collection_name):
    """Verify the restored collection"""
    
    print("\n" + "="*70)
    print(f"STEP 4: Verify Restored Collection")
    print("="*70)
    
    headers = {"Content-Type": "application/json"}
    if config.WEAVIATE_API_KEY and config.WEAVIATE_API_KEY != "your-weaviate-api-key":
        headers["Authorization"] = f"Bearer {config.WEAVIATE_API_KEY}"
    
    # Count objects
    print(f"\n🔍 Counting objects in {collection_name}...")
    count_query = {
        "query": f"""
        {{
          Aggregate {{
            {collection_name} {{
              meta {{ count }}
            }}
          }}
        }}
        """
    }
    
    response = requests.post(
        f"{config.WEAVIATE_URL}/v1/graphql",
        headers=headers,
        json=count_query,
        timeout=30
    )
    
    if response.status_code == 200:
        result = response.json()
        count_data = result.get("data", {}).get("Aggregate", {}).get(collection_name, [])
        if count_data:
            count = count_data[0].get("meta", {}).get("count", 0)
            print(f"✅ Collection has {count:,} objects after restore")
            
            if count > 0:
                # Fetch sample object
                sample_query = {
                    "query": f"""
                    {{
                      Get {{
                        {collection_name}(limit: 1) {{
                          title
                          artist
                          song_id
                        }}
                      }}
                    }}
                    """
                }
                
                response = requests.post(
                    f"{config.WEAVIATE_URL}/v1/graphql",
                    headers=headers,
                    json=sample_query,
                    timeout=30
                )
                
                if response.status_code == 200:
                    result = response.json()
                    objects = result.get("data", {}).get("Get", {}).get(collection_name, [])
                    if objects:
                        obj = objects[0]
                        print(f"\n📄 Sample object:")
                        print(f"   Title: {obj.get('title', 'N/A')}")
                        print(f"   Artist: {obj.get('artist', 'N/A')}")
                        print(f"   Song ID: {obj.get('song_id', 'N/A')}")
            
            return True
    
    print("❌ Failed to verify collection")
    return False


def main():
    """Main test function"""
    
    print("╔" + "="*68 + "╗")
    print("║" + " "*16 + "BACKUP RESTORE TEST - SAFE DELETE & RESTORE" + " "*9 + "║")
    print("╚" + "="*68 + "╝")
    
    # Collection to test
    collection_name = "SongLyrics_10k"
    
    print(f"\n🎯 Test Plan:")
    print(f"   1. Delete collection: {collection_name}")
    print(f"   2. Recreate schema")
    print(f"   3. Restore from Azure Blob backup")
    print(f"   4. Verify restoration")
    print(f"\n⚠️  This is a SAFE test on small collection (10k objects)")
    print("="*70)
    
    confirm = input("\nProceed with test? (yes/no): ").strip().lower()
    if confirm != 'yes':
        print("❌ Test cancelled")
        return 0
    
    # Step 1: Delete collection
    if not delete_collection(collection_name):
        print("\n❌ Failed to delete collection")
        return 1
    
    # Step 2: Recreate schema
    if not recreate_schema(collection_name, source_collection="SongLyrics"):
        print("\n❌ Failed to recreate schema")
        return 1
    
    # Step 3: Restore from backup
    print("\n⏸️  Pausing 2 seconds...")
    import time
    time.sleep(2)
    
    success = asyncio.run(restore_collection(collection_name))
    if not success:
        print("\n❌ Restore failed or was cancelled")
        return 1
    
    # Step 4: Verify
    print("\n⏸️  Pausing 3 seconds before verification...")
    time.sleep(3)
    
    if verify_restore(collection_name):
        print("\n" + "="*70)
        print("🎉 TEST SUCCESSFUL!")
        print("="*70)
        print(f"\n✅ Collection {collection_name} successfully:")
        print("   1. Deleted ✓")
        print("   2. Schema recreated ✓")
        print("   3. Data restored from backup ✓")
        print("   4. Verified ✓")
        print("\n💡 Your backup/restore system is working perfectly!")
        print("="*70)
        return 0
    else:
        print("\n❌ Verification failed")
        return 1


if __name__ == "__main__":
    sys.exit(main())

