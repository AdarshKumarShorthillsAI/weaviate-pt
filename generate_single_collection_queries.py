"""
Generate queries for testing SINGLE collection (SongLyrics with 1M data).
For automated performance testing across multiple limits.
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


def generate_bm25_query(query_text, limit, collection_name):
    """Generate BM25 search query for single collection"""
    return f"""
    {{
      Get {{
        {collection_name}(
          bm25: {{query: "{query_text}", properties: ["title", "lyrics"]}}
          limit: {limit}
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
      }}
    }}
    """


def generate_hybrid_query(query_text, query_vector, alpha, limit, collection_name):
    """Generate hybrid search query for single collection"""
    vector_str = json.dumps(query_vector)
    
    return f"""
    {{
      Get {{
        {collection_name}(
          hybrid: {{
            query: "{query_text}"
            alpha: {alpha}
            vector: {vector_str}
            properties: ["title", "lyrics"]
          }}
          limit: {limit}
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
      }}
    }}
    """


def generate_query_files(limit, collection_name, query_embeddings):
    """Generate all 4 query files for a specific limit"""
    
    # File 1: BM25
    bm25_queries = []
    for query_text in SEARCH_QUERIES:
        query_data = {
            "query_text": query_text,
            "search_type": "bm25",
            "limit": limit,
            "graphql": generate_bm25_query(query_text, limit, collection_name)
        }
        bm25_queries.append(query_data)
    
    with open(f"queries_bm25_{limit}.json", "w") as f:
        json.dump(bm25_queries, f, indent=2)
    
    # File 2: Hybrid 0.1
    hybrid_01_queries = []
    for query_text in SEARCH_QUERIES:
        query_data = {
            "query_text": query_text,
            "search_type": "hybrid_0.1",
            "alpha": 0.1,
            "limit": limit,
            "graphql": generate_hybrid_query(
                query_text, query_embeddings[query_text], 0.1, limit, collection_name
            )
        }
        hybrid_01_queries.append(query_data)
    
    with open(f"queries_hybrid_01_{limit}.json", "w") as f:
        json.dump(hybrid_01_queries, f, indent=2)
    
    # File 3: Hybrid 0.9
    hybrid_09_queries = []
    for query_text in SEARCH_QUERIES:
        query_data = {
            "query_text": query_text,
            "search_type": "hybrid_0.9",
            "alpha": 0.9,
            "limit": limit,
            "graphql": generate_hybrid_query(
                query_text, query_embeddings[query_text], 0.9, limit, collection_name
            )
        }
        hybrid_09_queries.append(query_data)
    
    with open(f"queries_hybrid_09_{limit}.json", "w") as f:
        json.dump(hybrid_09_queries, f, indent=2)
    
    # File 4: Mixed
    mixed_queries = []
    for i, query_text in enumerate(SEARCH_QUERIES):
        if i < 10:
            # BM25
            query_data = {
                "query_text": query_text,
                "search_type": "bm25",
                "limit": limit,
                "graphql": generate_bm25_query(query_text, limit, collection_name)
            }
        elif i < 20:
            # Hybrid 0.1
            query_data = {
                "query_text": query_text,
                "search_type": "hybrid_0.1",
                "alpha": 0.1,
                "limit": limit,
                "graphql": generate_hybrid_query(
                    query_text, query_embeddings[query_text], 0.1, limit, collection_name
                )
            }
        else:
            # Hybrid 0.9
            query_data = {
                "query_text": query_text,
                "search_type": "hybrid_0.9",
                "alpha": 0.9,
                "limit": limit,
                "graphql": generate_hybrid_query(
                    query_text, query_embeddings[query_text], 0.9, limit, collection_name
                )
            }
        
        mixed_queries.append(query_data)
    
    with open(f"queries_mixed_{limit}.json", "w") as f:
        json.dump(mixed_queries, f, indent=2)
    
    return True


def main():
    """Generate queries for all limits"""
    collection_name = config.WEAVIATE_CLASS_NAME  # Default: SongLyrics
    limits = [10, 50, 100, 150, 200]
    
    print("=" * 70)
    print("SINGLE COLLECTION QUERY GENERATOR")
    print("=" * 70)
    print(f"\nCollection: {collection_name}")
    print(f"Limits: {limits}")
    print(f"Queries per file: {len(SEARCH_QUERIES)}")
    print("=" * 70)
    
    # Generate embeddings once
    print("\n📊 Step 1: Generating embeddings (one-time)...")
    query_embeddings = {}
    for i, query in enumerate(SEARCH_QUERIES, 1):
        print(f"  [{i}/30] Embedding: '{query}'... ", end='', flush=True)
        embedding = get_embedding_for_query(query)
        if embedding:
            query_embeddings[query] = embedding
            print(f"✓")
        else:
            print("❌ Failed")
            return 1
    
    print(f"\n✅ All {len(query_embeddings)} embeddings generated!")
    
    # Generate query files for each limit
    print("\n📝 Step 2: Generating query files for all limits...")
    for limit in limits:
        print(f"\n  Limit {limit}:")
        if generate_query_files(limit, collection_name, query_embeddings):
            print(f"    ✅ queries_bm25_{limit}.json")
            print(f"    ✅ queries_hybrid_01_{limit}.json")
            print(f"    ✅ queries_hybrid_09_{limit}.json")
            print(f"    ✅ queries_mixed_{limit}.json")
    
    print("\n" + "=" * 70)
    print("✅ All query files generated!")
    print("=" * 70)
    print(f"\nGenerated {len(limits) * 4} query files")
    print("Ready for automated testing!")
    print("=" * 70)
    
    return 0


if __name__ == "__main__":
    sys.exit(main())

