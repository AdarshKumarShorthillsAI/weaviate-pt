"""
Quick verification script to test configuration before running the main processor.
Tests connectivity to OpenAI and Weaviate.
"""

import sys
from openai import OpenAI, AzureOpenAI
import weaviate
import config

def test_openai():
    """Test OpenAI API connection"""
    if config.USE_AZURE_OPENAI:
        print("Testing Azure OpenAI connection...")
        try:
            client = AzureOpenAI(
                api_key=config.AZURE_OPENAI_API_KEY,
                azure_endpoint=config.AZURE_OPENAI_ENDPOINT,
                api_version=config.AZURE_OPENAI_API_VERSION
            )
            # Try a simple embedding request to verify deployment
            response = client.embeddings.create(
                model=config.AZURE_OPENAI_DEPLOYMENT_NAME,
                input="test"
            )
            print("✅ Azure OpenAI connection successful!")
            print(f"   Endpoint: {config.AZURE_OPENAI_ENDPOINT}")
            print(f"   Deployment: {config.AZURE_OPENAI_DEPLOYMENT_NAME}")
            print(f"   API Version: {config.AZURE_OPENAI_API_VERSION}")
            print(f"   Embedding dimension: {len(response.data[0].embedding)}")
            return True
        except Exception as e:
            print(f"❌ Azure OpenAI connection failed: {e}")
            print("   Please check your Azure OpenAI settings in config.py:")
            print(f"   - AZURE_OPENAI_API_KEY")
            print(f"   - AZURE_OPENAI_ENDPOINT")
            print(f"   - AZURE_OPENAI_DEPLOYMENT_NAME")
            return False
    else:
        print("Testing OpenAI connection...")
        try:
            client = OpenAI(api_key=config.OPENAI_API_KEY)
            # Try to get models list
            models = client.models.list()
            print("✅ OpenAI connection successful!")
            print(f"   Model to use: {config.OPENAI_MODEL}")
            return True
        except Exception as e:
            print(f"❌ OpenAI connection failed: {e}")
            print("   Please check your OPENAI_API_KEY in config.py")
            return False

def test_weaviate():
    """Test Weaviate connection"""
    print("\nTesting Weaviate connection...")
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
            client = weaviate.connect_to_local(
                host=host,
                port=port,
                grpc_port=port + 1,
                headers={"X-OpenAI-Api-Key": config.WEAVIATE_API_KEY} if use_auth else None,
                skip_init_checks=True
            )
        else:
            # Remote connection (custom URL)
            from weaviate.connect import ConnectionParams
            
            client = weaviate.WeaviateClient(
                connection_params=ConnectionParams.from_url(
                    url=config.WEAVIATE_URL,
                    grpc_port=port + 1
                ),
                auth_client_secret=weaviate.auth.AuthApiKey(config.WEAVIATE_API_KEY) if use_auth else None,
                skip_init_checks=True
            )
            client.connect()
        
        # Test if server is reachable
        if client.is_ready():
            print("✅ Weaviate connection successful!")
            print(f"   URL: {config.WEAVIATE_URL}")
            
            # Check if collection exists
            if client.collections.exists(config.WEAVIATE_CLASS_NAME):
                print(f"   ✅ Collection '{config.WEAVIATE_CLASS_NAME}' exists and ready")
                print("      Existing data will be preserved, new data will be added")
            else:
                print(f"   ⚠️  Collection '{config.WEAVIATE_CLASS_NAME}' does not exist")
                print("      Run 'python create_weaviate_schema.py' to create it")
            
            client.close()
            return True
        else:
            print("❌ Weaviate server not ready")
            client.close()
            return False
    except Exception as e:
        print(f"❌ Weaviate connection failed: {e}")
        print(f"   URL: {config.WEAVIATE_URL}")
        print("   Please check your WEAVIATE_URL and WEAVIATE_API_KEY in config.py")
        return False

def test_csv():
    """Test CSV file accessibility"""
    print("\nTesting CSV file...")
    try:
        import os
        if not os.path.exists(config.CSV_FILE_PATH):
            print(f"❌ CSV file not found: {config.CSV_FILE_PATH}")
            return False
        
        # Try to read first row
        import pandas as pd
        df = pd.read_csv(config.CSV_FILE_PATH, nrows=1)
        print(f"✅ CSV file accessible!")
        print(f"   Path: {config.CSV_FILE_PATH}")
        print(f"   Columns: {list(df.columns)}")
        
        # Check if expected columns exist
        expected_cols = set(config.CSV_COLUMNS)
        actual_cols = set(df.columns)
        missing = expected_cols - actual_cols
        if missing:
            print(f"   ⚠️  Missing columns: {missing}")
        
        return True
    except Exception as e:
        print(f"❌ CSV file test failed: {e}")
        return False

def main():
    """Run all verification tests"""
    print("=" * 60)
    print("Setup Verification")
    print("=" * 60)
    
    results = []
    results.append(("OpenAI", test_openai()))
    results.append(("Weaviate", test_weaviate()))
    results.append(("CSV File", test_csv()))
    
    print("\n" + "=" * 60)
    print("Summary")
    print("=" * 60)
    
    all_passed = all(result for _, result in results)
    
    for name, passed in results:
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"{name:20} {status}")
    
    print("=" * 60)
    
    if all_passed:
        print("\n🎉 All tests passed! You can now run: python process_lyrics.py")
        return 0
    else:
        print("\n⚠️  Some tests failed. Please fix the issues above before proceeding.")
        return 1

if __name__ == "__main__":
    sys.exit(main())

