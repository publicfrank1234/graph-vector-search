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
- main.py: Main script for setting up the environment, querying, and performing search.
- milvus_utils.py: Utility functions for interacting with Milvus.
- neo4j_utils.py: Utility functions for interacting with Neo4j.
- data/wikipedia_content.json: Current data file.
- data/get_data.py: Script to fetch and save Wikipedia content as JSON.
- data/bm25_model.pkl: Pretrained BM25 model using existing data to speed up hybrid search.

## Data Storage
### Neo4j
Neo4j is used as the primary data store for the actual text content. Each document and paragraph has a unique ID which is stored in Neo4j. The structure in Neo4j is:

Page nodes represent the individual Wikipedia pages.
Paragraph nodes represent the paragraphs within each page.
HAS_PARAGRAPH relationships link Pages to their Paragraphs.

![Alt text](./data/image.png)

### Milvus
Milvus is used as the vector index to perform fast similarity searches on paragraph embeddings. Each paragraph's embedding is stored in Milvus with the same ID as the one in Neo4j. This allows linking the results from Milvus back to the actual content in Neo4j.

### Linking Neo4j and Milvus
Paragraph IDs in Neo4j are the same as those in Milvus.
During a search, Milvus provides the IDs of the relevant paragraphs, which are then used to fetch the actual content from Neo4j.


## How to run 
### Setup
To set up the environment, load data into Neo4j and Milvus:

```bash
python main.py setup
```

### Normal Query
To perform a vector-based search:
```bash
python main.py query "<your query text>"
```

### Hybrid Query
To perform a hybrid search combining vector embeddings and BM25 using RRF:

```bash
python main.py hybrid_query "<your query text>" 
``` 
Note: The hybrid query can be slow. A locally trained BM25 model is included (data/bm25_model.pkl). If deleted, it will be retrained from scratch, which takes a long time.

### Cleanup
To delete all data from Neo4j and Milvus:
```bash
python main.py cleanup
```

### Data Preparation
To fetch and save Wikipedia content as JSON:
```bash
python data/get_data.py
```
This will extract content from a list of Wikipedia URLs, chunk the text by paragraphs, and save it as wikipedia_content.json.