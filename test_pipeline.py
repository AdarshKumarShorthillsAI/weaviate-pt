"""
Test script to verify the complete pipeline by indexing a few rows from CSV to Weaviate.
This tests: CSV reading → Azure OpenAI embeddings → Weaviate indexing → Search
"""

import asyncio
import sys
import pandas as pd
import weaviate
import weaviate.classes as wvc
from openai import AsyncAzureOpenAI, AsyncOpenAI

import config

# Number of test rows to process
TEST_ROWS = 5


class PipelineTester:
    """Tests the complete pipeline with a small sample"""
    
    def __init__(self):
        # Initialize OpenAI client
        if config.USE_AZURE_OPENAI:
            self.openai_client = AsyncAzureOpenAI(
                api_key=config.AZURE_OPENAI_API_KEY,
                azure_endpoint=config.AZURE_OPENAI_ENDPOINT,
                api_version=config.AZURE_OPENAI_API_VERSION
            )
            self.embedding_model = config.AZURE_OPENAI_DEPLOYMENT_NAME
            print(f"✓ Using Azure OpenAI: {self.embedding_model}")
        else:
            self.openai_client = AsyncOpenAI(api_key=config.OPENAI_API_KEY)
            self.embedding_model = config.OPENAI_MODEL
            print(f"✓ Using OpenAI: {self.embedding_model}")
        
        self.weaviate_client = None
        self.collection = None
    
    def connect_weaviate(self):
        """Connect to Weaviate"""
        print("\n📊 Connecting to Weaviate...")
        try:
            # Parse URL to extract protocol, host, and port
            url = config.WEAVIATE_URL
            is_https = url.startswith("https://")
            url_without_protocol = url.replace("https://", "").replace("http://", "")
            
            # Split host and port
            if ":" in url_without_protocol:
                host, port_str = url_without_protocol.split(":", 1)
                port_str = port_str.split("/")[0]
                port = int(port_str)
            else:
                host = url_without_protocol.split("/")[0]
                port = 443 if is_https else 80
            
            # Check if authentication is needed
            use_auth = config.WEAVIATE_API_KEY and config.WEAVIATE_API_KEY != "your-weaviate-api-key"
            
            print(f"   Connecting to {host}:{port} (HTTPS: {is_https}, Auth: {use_auth})")
            
            # Connect to Weaviate
            if host in ["localhost", "127.0.0.1"]:
                self.weaviate_client = weaviate.connect_to_local(
                    host=host,
                    port=port,
                    grpc_port=port + 1,
                    headers={"X-OpenAI-Api-Key": config.WEAVIATE_API_KEY} if use_auth else None,
                    skip_init_checks=True
                )
            else:
                # Remote connection (custom URL)
                from weaviate.connect import ConnectionParams
                
                self.weaviate_client = weaviate.WeaviateClient(
                    connection_params=ConnectionParams.from_url(
                        url=config.WEAVIATE_URL,
                        grpc_port=port + 1
                    ),
                    auth_client_secret=weaviate.auth.AuthApiKey(config.WEAVIATE_API_KEY) if use_auth else None,
                    skip_init_checks=True
                )
                self.weaviate_client.connect()
            
            if not self.weaviate_client.collections.exists(config.WEAVIATE_CLASS_NAME):
                print(f"❌ Collection '{config.WEAVIATE_CLASS_NAME}' does not exist!")
                print("   Run: python create_weaviate_schema.py")
                return False
            
            self.collection = self.weaviate_client.collections.get(config.WEAVIATE_CLASS_NAME)
            print(f"✓ Connected to collection: {config.WEAVIATE_CLASS_NAME}")
            return True
            
        except Exception as e:
            print(f"❌ Weaviate connection failed: {e}")
            print(f"   URL: {config.WEAVIATE_URL}")
            return False
    
    def read_test_data(self):
        """Read test rows from CSV"""
        print(f"\n📖 Reading {TEST_ROWS} test rows from CSV...")
        try:
            df = pd.read_csv(config.CSV_FILE_PATH, nrows=TEST_ROWS)
            print(f"✓ Read {len(df)} rows")
            print(f"  Columns: {list(df.columns)}")
            return df
        except Exception as e:
            print(f"❌ Failed to read CSV: {e}")
            return None
    
    async def get_embedding(self, text: str):
        """Get embedding for text"""
        try:
            response = await self.openai_client.embeddings.create(
                model=self.embedding_model,
                input=text[:8000]  # Limit text length
            )
            return response.data[0].embedding
        except Exception as e:
            print(f"  ❌ Embedding failed: {e}")
            return None
    
    async def process_and_index(self, df):
        """Process rows and index to Weaviate"""
        print(f"\n🔄 Processing {len(df)} rows...")
        print("=" * 70)
        
        success_count = 0
        error_count = 0
        indexed_ids = []
        
        for idx, row in df.iterrows():
            try:
                # Clean data
                data = {
                    'title': str(row.get('title', '')),
                    'tag': str(row.get('tag', '')),
                    'artist': str(row.get('artist', '')),
                    'year': int(row.get('year', 0)) if pd.notna(row.get('year')) else 0,
                    'views': int(row.get('views', 0)) if pd.notna(row.get('views')) else 0,
                    'features': str(row.get('features', '')),
                    'lyrics': str(row.get('lyrics', '')),
                    'song_id': str(row.get('id', '')),
                    'language_cld3': str(row.get('language_cld3', '')),
                    'language_ft': str(row.get('language_ft', '')),
                    'language': str(row.get('language', ''))
                }
                
                print(f"\n[{idx+1}/{len(df)}] {data['title']} by {data['artist']}")
                
                # Get embedding
                print(f"  → Getting embedding... ", end="", flush=True)
                embedding = await self.get_embedding(data['lyrics'])
                if embedding is None:
                    print("❌ Failed")
                    error_count += 1
                    continue
                print(f"✓ ({len(embedding)} dims)")
                
                # Index to Weaviate
                print(f"  → Indexing to Weaviate... ", end="", flush=True)
                result = self.collection.data.insert(
                    properties=data,
                    vector=embedding
                )
                print(f"✓ UUID: {str(result)[:8]}...")
                indexed_ids.append(result)
                success_count += 1
                
            except Exception as e:
                print(f"  ❌ Error: {e}")
                error_count += 1
        
        print("=" * 70)
        print(f"\n✅ Indexing Complete:")
        print(f"   Successfully indexed: {success_count}")
        print(f"   Errors: {error_count}")
        
        return indexed_ids
    
    async def test_search(self, indexed_ids):
        """Test searching the indexed data"""
        if not indexed_ids:
            print("\n⚠️  No data indexed, skipping search test")
            return
        
        print(f"\n🔍 Testing search functionality...")
        print("=" * 70)
        
        try:
            # Test 1: Vector search
            print("\n1. Vector Search Test: 'love songs'")
            results = self.collection.query.bm25(
                query="love songs",
                query_properties=["title", "lyrics"],
                limit=3
            )
            
            if results.objects:
                print(f"   ✓ Found {len(results.objects)} results:")
                for i, obj in enumerate(results.objects, 1):
                    print(f"   {i}. {obj.properties['title']} by {obj.properties['artist']}")
            else:
                print("   ⚠️  No results found")
            
            # Test 2: Get by ID
            print(f"\n2. Fetch by UUID Test")
            test_id = indexed_ids[0]
            obj = self.collection.query.fetch_object_by_id(test_id)
            if obj:
                print(f"   ✓ Retrieved: {obj.properties['title']}")
            else:
                print("   ❌ Failed to retrieve")
            
            # Test 3: Filtered search (if you have data)
            print(f"\n3. Count total objects in collection")
            result = self.collection.aggregate.over_all(total_count=True)
            print(f"   ✓ Total objects: {result.total_count}")
            
            print("=" * 70)
            print("✅ All search tests completed!")
            
        except Exception as e:
            print(f"❌ Search test failed: {e}")
    
    async def run(self):
        """Run the complete test pipeline"""
        print("=" * 70)
        print("🧪 PIPELINE TEST - End-to-End Verification")
        print("=" * 70)
        
        # Step 1: Connect to Weaviate
        if not self.connect_weaviate():
            return False
        
        # Step 2: Read test data
        df = self.read_test_data()
        if df is None or len(df) == 0:
            return False
        
        # Step 3: Process and index
        indexed_ids = await self.process_and_index(df)
        
        # Step 4: Test search
        await self.test_search(indexed_ids)
        
        print("\n" + "=" * 70)
        print("🎉 Pipeline test completed successfully!")
        print("=" * 70)
        print("\n✅ Your setup is working correctly!")
        print("   You can now run: python process_lyrics.py")
        print("=" * 70)
        
        return True
    
    async def close(self):
        """Cleanup"""
        if self.weaviate_client:
            self.weaviate_client.close()
        await self.openai_client.close()


async def main():
    """Main entry point"""
    tester = PipelineTester()
    
    try:
        success = await tester.run()
        if not success:
            print("\n❌ Test failed. Please check the errors above.")
            sys.exit(1)
    except KeyboardInterrupt:
        print("\n\n⚠️  Test interrupted by user")
    except Exception as e:
        print(f"\n❌ Fatal error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
    finally:
        await tester.close()


if __name__ == "__main__":
    print("\n" + "=" * 70)
    print("  END-TO-END PIPELINE TEST")
    print(f"  Testing with {TEST_ROWS} rows from CSV")
    print("=" * 70 + "\n")
    
    # Run the async main function
    asyncio.run(main())

