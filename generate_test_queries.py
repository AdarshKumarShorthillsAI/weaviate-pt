"""
Generate pre-built GraphQL queries for Weaviate performance testing.
Creates 4 files with 30 queries each for different search types.
Pre-generates embeddings for hybrid queries to avoid API calls during testing.
"""

import json
import sys
from openai_client import create_sync_openai_client
import config

# 30 diverse search queries for testing
SEARCH_QUERIES = [
    "love and heartbreak",
    "summer party vibes",
    "feeling alone tonight",
    "dance all night long",
    "broken dreams and hope",
    "city lights at midnight",
    "memories of yesterday",
    "living life to fullest",
    "chasing dreams forever",
    "never give up fighting",
    "friendship and loyalty",
    "money power respect",
    "family comes first always",
    "trust nobody believe yourself",
    "hustle grind every day",
    "success and motivation",
    "romantic love story",
    "pain and suffering",
    "celebration and joy",
    "freedom and liberty",
    "hope for better tomorrow",
    "struggle and perseverance",
    "peace and tranquility",
    "anger and revenge",
    "happiness and laughter",
    "sadness and tears",
    "victory and triumph",
    "loss and defeat",
    "passion and desire",
    "fear and courage"
]

# All collections to search
COLLECTIONS = [
    "SongLyrics",
    "SongLyrics_400k",
    "SongLyrics_200k",
    "SongLyrics_50k",
    "SongLyrics_30k",
    "SongLyrics_20k",
    "SongLyrics_15k",
    "SongLyrics_12k",
    "SongLyrics_10k"
]


def get_embedding_for_query(query_text):
    """Get embedding for a query using Azure OpenAI"""
    try:
        client, model = create_sync_openai_client()
        response = client.embeddings.create(
            model=model,
            input=query_text
        )
        return response.data[0].embedding
    except Exception as e:
        print(f"Error getting embedding for '{query_text}': {e}")
        return None


def generate_bm25_multi_collection_query(query_text):
    """Generate BM25 search query for ALL collections in single request"""
    collection_queries = []
    
    for collection in COLLECTIONS:
        collection_query = f"""
        {collection}(
          bm25: {{query: "{query_text}", properties: ["title", "lyrics"]}}
          limit: 200
        ) {{
          title
          tag
          artist
          year
          views
          features
          lyrics
          song_id
          language_cld3
          language_ft
          language
          _additional {{
            score
          }}
        }}
        """
        collection_queries.append(collection_query)
    
    # Combine all collection queries into single GraphQL query
    all_collections = "\n        ".join(collection_queries)
    
    return f"""
    {{
      Get {{
        {all_collections}
      }}
    }}
    """


def generate_hybrid_multi_collection_query(query_text, query_vector, alpha):
    """Generate hybrid search query for ALL collections in single request"""
    # Format vector as JSON array
    vector_str = json.dumps(query_vector)
    
    collection_queries = []
    
    for collection in COLLECTIONS:
        collection_query = f"""
        {collection}(
          hybrid: {{
            query: "{query_text}"
            alpha: {alpha}
            vector: {vector_str}
          }}
          limit: 200
        ) {{
          title
          tag
          artist
          year
          views
          features
          lyrics
          song_id
          language_cld3
          language_ft
          language
          _additional {{
            score
          }}
        }}
        """
        collection_queries.append(collection_query)
    
    # Combine all collection queries into single GraphQL query
    all_collections = "\n        ".join(collection_queries)
    
    return f"""
    {{
      Get {{
        {all_collections}
      }}
    }}
    """


def generate_all_query_files():
    """Generate all 4 query files with pre-computed embeddings"""
    
    print("=" * 70)
    print("PERFORMANCE TEST QUERY GENERATOR")
    print("=" * 70)
    print(f"\nGenerating queries for {len(SEARCH_QUERIES)} search terms")
    print(f"Across {len(COLLECTIONS)} collections")
    print(f"Total queries per file: {len(SEARCH_QUERIES)}")
    print("=" * 70)
    
    # Pre-generate embeddings for all queries (only once!)
    print("\n📊 Step 1: Generating embeddings for hybrid queries...")
    print("(This calls Azure OpenAI 30 times - only done once during setup)")
    
    query_embeddings = {}
    for i, query in enumerate(SEARCH_QUERIES, 1):
        print(f"  [{i}/30] Embedding: '{query}'... ", end='', flush=True)
        embedding = get_embedding_for_query(query)
        if embedding:
            query_embeddings[query] = embedding
            print(f"✓ ({len(embedding)} dims)")
        else:
            print("❌ Failed")
            return False
    
    print(f"\n✅ All {len(query_embeddings)} embeddings generated!")
    
    # File 1: BM25 queries
    print("\n📝 Step 2: Generating BM25 query file...")
    bm25_queries = []
    for query_text in SEARCH_QUERIES:
        query_data = {
            "query_text": query_text,
            "search_type": "bm25",
            "graphql": generate_bm25_multi_collection_query(query_text)
        }
        bm25_queries.append(query_data)
    
    with open("queries_bm25.json", "w") as f:
        json.dump(bm25_queries, f, indent=2)
    
    print(f"✅ Created: queries_bm25.json ({len(bm25_queries)} multi-collection queries)")
    
    # File 2: Hybrid alpha=0.1
    print("\n📝 Step 3: Generating Hybrid (alpha=0.1) query file...")
    hybrid_01_queries = []
    for query_text in SEARCH_QUERIES:
        query_data = {
            "query_text": query_text,
            "search_type": "hybrid_0.1",
            "alpha": 0.1,
            "graphql": generate_hybrid_multi_collection_query(
                query_text, query_embeddings[query_text], 0.1
            )
        }
        hybrid_01_queries.append(query_data)
    
    with open("queries_hybrid_01.json", "w") as f:
        json.dump(hybrid_01_queries, f, indent=2)
    
    print(f"✅ Created: queries_hybrid_01.json ({len(hybrid_01_queries)} multi-collection queries)")
    
    # File 3: Hybrid alpha=0.9
    print("\n📝 Step 4: Generating Hybrid (alpha=0.9) query file...")
    hybrid_09_queries = []
    for query_text in SEARCH_QUERIES:
        query_data = {
            "query_text": query_text,
            "search_type": "hybrid_0.9",
            "alpha": 0.9,
            "graphql": generate_hybrid_multi_collection_query(
                query_text, query_embeddings[query_text], 0.9
            )
        }
        hybrid_09_queries.append(query_data)
    
    with open("queries_hybrid_09.json", "w") as f:
        json.dump(hybrid_09_queries, f, indent=2)
    
    print(f"✅ Created: queries_hybrid_09.json ({len(hybrid_09_queries)} multi-collection queries)")
    
    # File 4: Mixed (all three types)
    print("\n📝 Step 5: Generating Mixed query file...")
    mixed_queries = []
    
    # Distribute 30 queries: 10 BM25, 10 Hybrid 0.1, 10 Hybrid 0.9
    for i, query_text in enumerate(SEARCH_QUERIES):
        if i < 10:
            # BM25
            query_data = {
                "query_text": query_text,
                "search_type": "bm25",
                "graphql": generate_bm25_multi_collection_query(query_text)
            }
        
        elif i < 20:
            # Hybrid 0.1
            query_data = {
                "query_text": query_text,
                "search_type": "hybrid_0.1",
                "alpha": 0.1,
                "graphql": generate_hybrid_multi_collection_query(
                    query_text, query_embeddings[query_text], 0.1
                )
            }
        
        else:
            # Hybrid 0.9
            query_data = {
                "query_text": query_text,
                "search_type": "hybrid_0.9",
                "alpha": 0.9,
                "graphql": generate_hybrid_multi_collection_query(
                    query_text, query_embeddings[query_text], 0.9
                )
            }
        
        mixed_queries.append(query_data)
    
    with open("queries_mixed.json", "w") as f:
        json.dump(mixed_queries, f, indent=2)
    
    print(f"✅ Created: queries_mixed.json ({len(mixed_queries)} multi-collection queries)")
    
    # Summary
    print("\n" + "=" * 70)
    print("SUMMARY")
    print("=" * 70)
    print(f"✅ Generated 4 query files:")
    print(f"   1. queries_bm25.json       - 30 BM25 queries")
    print(f"   2. queries_hybrid_01.json  - 30 Hybrid (alpha=0.1) queries")
    print(f"   3. queries_hybrid_09.json  - 30 Hybrid (alpha=0.9) queries")
    print(f"   4. queries_mixed.json      - 10 BM25 + 10 Hybrid 0.1 + 10 Hybrid 0.9")
    print(f"\n📊 Each query searches {len(COLLECTIONS)} collections")
    print(f"   Returns 200 results per collection")
    print(f"   Total results per query: {200 * len(COLLECTIONS):,}")
    print("\n💡 Embeddings pre-generated (stored in files)")
    print("   No API calls needed during performance testing!")
    print("=" * 70)
    
    return True


if __name__ == "__main__":
    success = generate_all_query_files()
    sys.exit(0 if success else 1)

