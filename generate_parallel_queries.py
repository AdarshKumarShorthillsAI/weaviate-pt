"""
Generate queries for PARALLEL testing approach.
Each collection gets a separate query (not combined in single GraphQL request).
Client will send 9 parallel requests and merge results.
"""

import json
import sys
from openai_client import create_sync_openai_client
import config

# 30 diverse search queries
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

# All collections
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
    """Get embedding for query"""
    try:
        client, model = create_sync_openai_client()
        response = client.embeddings.create(model=model, input=query_text)
        return response.data[0].embedding
    except Exception as e:
        print(f"Error: {e}")
        return None


def generate_bm25_query(query_text, limit, collection_name):
    """Generate BM25 query for single collection"""
    return {
        "collection": collection_name,
        "graphql": f"""
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
              _additional {{ score }}
            }}
          }}
        }}
        """
    }


def generate_hybrid_query(query_text, vector, alpha, limit, collection_name):
    """Generate hybrid query for single collection"""
    vector_str = json.dumps(vector)
    return {
        "collection": collection_name,
        "graphql": f"""
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
              _additional {{ score }}
            }}
          }}
        }}
        """
    }


def generate_parallel_files(limit):
    """Generate parallel query files for specific limit"""
    
    # Get embeddings
    print(f"\n📊 Generating embeddings for limit {limit}...")
    query_embeddings = {}
    for i, query in enumerate(SEARCH_QUERIES, 1):
        print(f"  [{i}/30] {query}...", end=' ', flush=True)
        emb = get_embedding_for_query(query)
        if emb:
            query_embeddings[query] = emb
            print("✓")
        else:
            print("❌")
            return False
    
    # File 1: BM25 Parallel
    bm25_queries = []
    for query_text in SEARCH_QUERIES:
        query_data = {
            "query_text": query_text,
            "search_type": "bm25",
            "limit": limit,
            "queries": [generate_bm25_query(query_text, limit, col) for col in COLLECTIONS]
        }
        bm25_queries.append(query_data)
    
    with open(f"queries_parallel_bm25_{limit}.json", "w") as f:
        json.dump(bm25_queries, f, indent=2)
    print(f"✅ queries_parallel_bm25_{limit}.json")
    
    # File 2: Hybrid 0.1 Parallel
    hybrid_01_queries = []
    for query_text in SEARCH_QUERIES:
        query_data = {
            "query_text": query_text,
            "search_type": "hybrid_0.1",
            "alpha": 0.1,
            "limit": limit,
            "queries": [generate_hybrid_query(query_text, query_embeddings[query_text], 0.1, limit, col) for col in COLLECTIONS]
        }
        hybrid_01_queries.append(query_data)
    
    with open(f"queries_parallel_hybrid_01_{limit}.json", "w") as f:
        json.dump(hybrid_01_queries, f, indent=2)
    print(f"✅ queries_parallel_hybrid_01_{limit}.json")
    
    # File 3: Hybrid 0.9 Parallel
    hybrid_09_queries = []
    for query_text in SEARCH_QUERIES:
        query_data = {
            "query_text": query_text,
            "search_type": "hybrid_0.9",
            "alpha": 0.9,
            "limit": limit,
            "queries": [generate_hybrid_query(query_text, query_embeddings[query_text], 0.9, limit, col) for col in COLLECTIONS]
        }
        hybrid_09_queries.append(query_data)
    
    with open(f"queries_parallel_hybrid_09_{limit}.json", "w") as f:
        json.dump(hybrid_09_queries, f, indent=2)
    print(f"✅ queries_parallel_hybrid_09_{limit}.json")
    
    # File 4: Mixed Parallel
    mixed_queries = []
    for i, query_text in enumerate(SEARCH_QUERIES):
        if i < 10:  # BM25
            query_data = {
                "query_text": query_text,
                "search_type": "bm25",
                "limit": limit,
                "queries": [generate_bm25_query(query_text, limit, col) for col in COLLECTIONS]
            }
        elif i < 20:  # Hybrid 0.1
            query_data = {
                "query_text": query_text,
                "search_type": "hybrid_0.1",
                "alpha": 0.1,
                "limit": limit,
                "queries": [generate_hybrid_query(query_text, query_embeddings[query_text], 0.1, limit, col) for col in COLLECTIONS]
            }
        else:  # Hybrid 0.9
            query_data = {
                "query_text": query_text,
                "search_type": "hybrid_0.9",
                "alpha": 0.9,
                "limit": limit,
                "queries": [generate_hybrid_query(query_text, query_embeddings[query_text], 0.9, limit, col) for col in COLLECTIONS]
            }
        mixed_queries.append(query_data)
    
    with open(f"queries_parallel_mixed_{limit}.json", "w") as f:
        json.dump(mixed_queries, f, indent=2)
    print(f"✅ queries_parallel_mixed_{limit}.json")
    
    return True


def main():
    """Generate parallel query files for all limits"""
    limits = [10, 50, 100, 150, 200]
    
    print("=" * 70)
    print("PARALLEL QUERY GENERATOR")
    print("=" * 70)
    print(f"Limits: {limits}")
    print(f"Collections: {len(COLLECTIONS)}")
    print(f"Queries: {len(SEARCH_QUERIES)}")
    print("=" * 70)
    
    for limit in limits:
        print(f"\n🔄 Generating for limit {limit}...")
        if not generate_parallel_files(limit):
            return 1
    
    print("\n" + "=" * 70)
    print(f"✅ Generated {len(limits) * 4} parallel query files")
    print("=" * 70)
    return 0


if __name__ == "__main__":
    sys.exit(main())

