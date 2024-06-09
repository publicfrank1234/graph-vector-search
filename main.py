import os
import pickle

from milvus_utils import (
    connect_to_milvus,
    create_bm25_model,
    delete_collections_from_milvus,
    save_vectors_to_milvus,
    search_hybrid_in_milvus,
    search_vectors_in_milvus,
    vectorize_paragraphs,
)
from neo4j_utils import (
    connect_to_neo4j,
    delete_all_data_from_neo4j,
    fetch_paragraphs_from_neo4j,
    save_to_neo4j,
)


def load_json_data(filename):
    import json

    with open(filename, "r") as file:
        return json.load(file)


def search_vectors_and_retrieve_data(graph, query, limit=5):
    results = search_vectors_in_milvus(query, limit)

    for hits in results:
        for hit in hits:
            milvus_id = hit.id
            distance = hit.distance
            paragraph = graph.run(
                "MATCH (p:Paragraph) WHERE ID(p) = $milvus_id RETURN p.content",
                milvus_id=milvus_id,
            ).evaluate()
            print(f"Milvus/Neo4j ID: {milvus_id}, Distance: {distance}")
            print(f"Paragraph: {paragraph}\n")


def search_hybrid_and_retrieve_data(graph, query, bm25, limit=5):
    paragraphs = fetch_paragraphs_from_neo4j(graph)
    results = search_hybrid_in_milvus(query, paragraphs, bm25, limit)

    for neo4j_id, score in results:
        paragraph = graph.run(
            "MATCH (p:Paragraph) WHERE ID(p) = $neo4j_id RETURN p.content",
            neo4j_id=neo4j_id,
        ).evaluate()
        print(f"Neo4j ID: {neo4j_id}, Score: {score}")
        print(f"Paragraph: {paragraph}\n")


def main():
    import sys

    if len(sys.argv) < 2:
        print("Usage: python main.py <setup|query|hybrid_query|cleanup> [query_text]")
        return

    command = sys.argv[1]

    # Connect to Neo4j and Milvus
    graph = connect_to_neo4j()
    connect_to_milvus()

    if command == "setup":
        # Load the JSON data
        json_filename = "./data/wikipedia_content.json"
        data = load_json_data(json_filename)

        # Save the data to Neo4j
        save_to_neo4j(graph, data)

        # Fetch paragraphs from Neo4j
        paragraphs = fetch_paragraphs_from_neo4j(graph)

        # Vectorize the paragraphs
        contents = [paragraph["content"] for paragraph in paragraphs]
        embeddings = vectorize_paragraphs(contents)

        # Save vectors to Milvus
        save_vectors_to_milvus(paragraphs, embeddings)

        print("Data saved to Milvus and linked with Neo4j")

    elif command == "query":
        if len(sys.argv) < 3:
            print("Usage: python main.py query <query_text>")
            return

        query_text = sys.argv[2]
        print(f"Searching for: {query_text}")

        # Perform the search and retrieve data
        search_vectors_and_retrieve_data(graph, query_text)

    elif command == "hybrid_query":
        if len(sys.argv) < 3:
            print("Usage: python main.py hybrid_query <query_text>")
            return

        query_text = sys.argv[2]
        print(f"Searching for: {query_text}")

        # Check if BM25 model exists
        bm25_model_path = "./data/bm25_model.pkl"
        if os.path.exists(bm25_model_path):
            with open(bm25_model_path, "rb") as f:
                bm25 = pickle.load(f)
        else:
            # Fetch paragraphs from Neo4j
            paragraphs = fetch_paragraphs_from_neo4j(graph)
            contents = [paragraph["content"] for paragraph in paragraphs]

            # Create BM25 model
            bm25 = create_bm25_model(contents)

            # Save the BM25 model for future use
            with open(bm25_model_path, "wb") as f:
                pickle.dump(bm25, f)

        # Perform the hybrid search and retrieve data
        search_hybrid_and_retrieve_data(graph, query_text, bm25)

    elif command == "cleanup":
        print("Cleaning up Neo4j and Milvus")

        # Delete data from Neo4j
        delete_all_data_from_neo4j(graph)

        # Delete collections from Milvus
        delete_collections_from_milvus()


if __name__ == "__main__":
    main()
