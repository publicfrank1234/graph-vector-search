from py2neo import Graph, Node, Relationship


def connect_to_neo4j():
    neo4j_url = "bolt://localhost:7687"
    neo4j_user = "neo4j"
    neo4j_password = "frankzhang123"  # Replace with your actual password
    graph = Graph(neo4j_url, auth=(neo4j_user, neo4j_password))
    print("Connected to Neo4j")
    return graph


def chunk_text_by_paragraph(text):
    sections = text.split("\n\n")
    paragraphs = []
    for section in sections:
        sub_paragraphs = section.split("\n")
        for sub_para in sub_paragraphs:
            if sub_para.strip():  # Ignore empty strings
                paragraphs.append(sub_para.strip())
    return paragraphs


def save_to_neo4j(graph, data):
    from datetime import datetime

    for entry in data:
        url = entry["url"]
        title = entry["title"]
        content = entry["content"]
        paragraphs = chunk_text_by_paragraph(content)
        timestamp = datetime.now().isoformat()

        print(f"Processing {title} with {len(paragraphs)} paragraphs.")

        page_node = Node("Page", url=url, title=title, created_at=timestamp)
        graph.create(page_node)
        print(f"Created Page node for {title}")

        for i, paragraph in enumerate(paragraphs):
            paragraph_node = Node(
                "Paragraph",
                id=f"{url}_para_{i+1}",
                content=paragraph,
                created_at=timestamp,
            )
            graph.create(paragraph_node)
            relationship = Relationship(page_node, "HAS_PARAGRAPH", paragraph_node)
            graph.create(relationship)
            print(f"Created Paragraph node {i+1} for {title} and relationship")

        if len(paragraphs) == 0:
            print(f"Warning: No paragraphs created for {title}")


def fetch_paragraphs_from_neo4j(graph):
    paragraphs = []
    result = graph.run(
        "MATCH (p:Paragraph) RETURN ID(p) as neo4j_id, p.content as content"
    )
    for record in result:
        paragraphs.append(
            {"neo4j_id": record["neo4j_id"], "content": record["content"]}
        )
    return paragraphs


def delete_all_data_from_neo4j(graph):
    graph.run("MATCH (p:Page)-[r:HAS_PARAGRAPH]->(para:Paragraph) DELETE r, para")
    graph.run("MATCH (p:Page) DELETE p")
