import numpy as np
from pymilvus import (
    Collection,
    CollectionSchema,
    DataType,
    FieldSchema,
    Index,
    connections,
    utility,
)
from rank_bm25 import BM25Okapi
from sentence_transformers import SentenceTransformer


def connect_to_milvus():
    connections.connect("default", host="localhost", port="19530")
    print("Connected to Milvus")


def vectorize_paragraphs(paragraphs):
    model = SentenceTransformer("paraphrase-MiniLM-L6-v2")
    embeddings = model.encode(paragraphs)
    return embeddings


def create_bm25_model(paragraphs):
    tokenized_paragraphs = [paragraph.split() for paragraph in paragraphs]
    bm25 = BM25Okapi(tokenized_paragraphs)
    return bm25


def save_vectors_to_milvus(paragraphs, embeddings):
    fields = [
        FieldSchema(name="neo4j_id", dtype=DataType.INT64, is_primary=True),
        FieldSchema(
            name="embedding", dtype=DataType.FLOAT_VECTOR, dim=len(embeddings[0])
        ),
    ]
    schema = CollectionSchema(fields, description="Paragraph Embeddings collection")

    collection_name = "paragraph_embeddings"
    collection = Collection(name=collection_name, schema=schema)

    if not collection.has_index():
        index_params = {
            "index_type": "IVF_FLAT",
            "metric_type": "L2",
            "params": {"nlist": 128},
        }
        Index(collection, "embedding", index_params)

    collection.load()

    neo4j_ids = [paragraph["neo4j_id"] for paragraph in paragraphs]
    embeddings_list = embeddings.tolist()

    data_to_insert = [
        neo4j_ids,
        embeddings_list,
    ]

    milvus_ids = collection.insert(data_to_insert)

    return milvus_ids


def search_vectors_in_milvus(query, limit=5):
    collection_name = "paragraph_embeddings"
    collection = Collection(name=collection_name)

    model = SentenceTransformer("paraphrase-MiniLM-L6-v2")
    query_embedding = model.encode([query])

    search_params = {"metric_type": "L2", "params": {"nprobe": 10}}
    results = collection.search(
        query_embedding.tolist(), "embedding", search_params, limit=limit
    )
    return results


def search_hybrid_in_milvus(query, paragraphs, bm25, limit=5):
    collection_name = "paragraph_embeddings"
    collection = Collection(name=collection_name)

    model = SentenceTransformer("paraphrase-MiniLM-L6-v2")
    query_embedding = model.encode([query])

    tokenized_query = query.split()

    search_params = {"metric_type": "L2", "params": {"nprobe": 10}}
    results_embedding = collection.search(
        query_embedding.tolist(), "embedding", search_params, limit=limit
    )

    combined_results = {}
    k = 60

    def rrf_score(rank):
        return 1 / (k + rank)

    for hits in results_embedding:
        for rank, hit in enumerate(hits):
            combined_results[hit.id] = combined_results.get(hit.id, 0) + rrf_score(
                rank + 1
            )

    # Compute BM25 scores on-the-fly
    bm25_scores = bm25.get_scores(tokenized_query)
    for rank, score in enumerate(bm25_scores):
        neo4j_id = paragraphs[rank]["neo4j_id"]
        combined_results[neo4j_id] = combined_results.get(neo4j_id, 0) + score

    sorted_results = sorted(
        combined_results.items(), key=lambda item: item[1], reverse=True
    )
    return sorted_results[:limit]


def fetch_paragraphs_from_milvus(limit=1000):
    collection_name = "paragraph_embeddings"
    collection = Collection(name=collection_name)

    results = collection.query(expr="", output_fields=["neo4j_id"], limit=limit)
    return results


def delete_collections_from_milvus():
    collection_names = ["paragraph_embeddings"]
    for collection_name in collection_names:
        if utility.has_collection(collection_name):
            collection = Collection(name=collection_name)
            collection.drop()
            print(f"Deleted collection: {collection_name}")
