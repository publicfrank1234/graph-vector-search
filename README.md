# Graph-Vector Search

This project integrates Neo4j, Milvus, and BM25 to demonstrate a search system 
1. normal embedding search 
2. hybrid search system combining vector embeddings and keyword-based search (using BM25). 

This repo sets up a graph database with vector index, performing normal and hybrid searches, and rerank results from both search results using other model, for example RRF.


## Prerequisites

- Python 3.12.3 
- Neo4j (docker)
- Milvus (docker)
- Required Python libraries:
  see requirements.txt

## Installation

1. **Clone the repository**:
   ```bash
   git clone https://github.com/publicfrank1234/graph-vector-search.git
   cd graph-vector-search
   ``` 

2. **Install Python dependencies**:

   ```bash
   pip install -r requirements.txt
   ```

3. **Ensure Neo4j and Milvus are running**:
   ```bash
   docker-compose up -d 
   ```

## Project Structure
main.py: Main script for setting up the environment, querying, and performing hybrid search.
milvus_utils.py: Utility functions for interacting with Milvus.
neo4j_utils.py: Utility functions for interacting with Neo4j.
data/wikipedia_content.json: Example data file (ensure this file is available or provide your own dataset).
data/get_data.py: Script to fetch and save Wikipedia content as JSON.
data/bm25_model.pkl: Pretrained BM25 model to speed up hybrid search.
