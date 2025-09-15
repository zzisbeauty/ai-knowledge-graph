from neo4j import GraphDatabase  
  
def export_to_neo4j(triples, neo4j_config):  
    """ 将三元组数据导出到Neo4j数据库  
    Args:  
        triples: 三元组列表  
        neo4j_config: Neo4j连接配置  
    """  
    # 连接Neo4j  
    driver = GraphDatabase.driver(  
        neo4j_config["uri"],   
        auth=(neo4j_config["username"], neo4j_config["password"])  
    )
      
    with driver.session() as session:  
        # 清空现有数据（可选）  
        session.run("MATCH (n) DETACH DELETE n")  
          
        # 创建节点和关系  
        for triple in triples:  
            session.run("""  
                MERGE (s:Entity {name: $subject})  
                MERGE (o:Entity {name: $object})  
                MERGE (s)-[r:RELATION {  
                    type: $predicate,  
                    chunk: $chunk,  
                    inferred: $inferred  
                }]->(o)  
            """,   
            subject=triple["subject"],  
            object=triple["object"],  
            predicate=triple["predicate"],  
            chunk=triple.get("chunk", 0),  
            inferred=triple.get("inferred", False)  
            )  

    driver.close()
