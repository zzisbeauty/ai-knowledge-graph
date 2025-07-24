""" 基于 conda env ai-kg 运行
"""

import os, pathlib
print("CWD :", os.getcwd())

from neo4j import GraphDatabase
import json

uri = "bolt://localhost:7687"
user = "neo4j"
password = "9NV84tLTcBLoVt"

driver = GraphDatabase.driver(uri, auth=(user, password))

def load_data(file_path):
    with open(file_path, 'r', encoding='utf-8') as f:
        return json.load(f)
    

def import_triples_dynamic_rel(triples):
    with driver.session() as session:
        for triple in triples:
            cypher = f"""
            MERGE (s:Entity {{name: $subject}})
            MERGE (o:Entity {{name: $object}})
            MERGE (s)-[:`{triple["predicate"]}`]->(o)
            """
            session.run(
                cypher,
                subject=triple["subject"],
                object=triple["object"]
            )



if __name__ == "__main__":
    # data = load_data("./data_graph_generate_result/gygm_graph.json")
    data = load_data("/home/git/ai-knowledge-graph/knowledge_graph.json")
    import_triples_dynamic_rel(data)
    driver.close()



"""
- gygm_graph.json data

1. 使用 Cypher 导入数据 /home/git/ai-knowledge-graph/data_graph_generate_result/gygm_graph.json

CALL apoc.load.json("file:///gygm_graph.json") YIELD value
WITH value
WHERE value.subject IS NOT NULL AND value.predicate IS NOT NULL AND value.object IS NOT NULL
MERGE (s:Entity {name: value.subject})
MERGE (o:Entity {name: value.object})
MERGE (s)-[r:REL {type: value.predicate}]->(o)

2. 基于 python 导入

...


- 其他数据集

...

"""