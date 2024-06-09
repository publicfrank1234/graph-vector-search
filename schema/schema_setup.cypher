// Constraints
CREATE CONSTRAINT ON (p:Page) ASSERT p.url IS UNIQUE;
CREATE CONSTRAINT ON (para:Paragraph) ASSERT para.id IS UNIQUE;

// Indexes
CREATE INDEX ON :Page(title);
CREATE INDEX ON :Paragraph(content);

// Documentation purposes
MATCH (p:Page), (para:Paragraph)
WHERE p.url = 'example_url' AND para.id = 'example_url_para_1'
CREATE (p)-[:HAS_PARAGRAPH]->(para);
