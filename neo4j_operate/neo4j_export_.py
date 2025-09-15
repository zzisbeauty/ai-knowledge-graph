#!/usr/bin/env python3  
""" Neo4j导入脚本 - 将AI知识图谱生成器的JSON数据导入Neo4j数据库； 基于 json 手动导入 neo4j 的脚本
"""  
  
import json  
import argparse  
from neo4j import GraphDatabase  
import sys  
  
class Neo4jImporter:  
    def __init__(self, uri, username, password):  
        """ 初始化Neo4j连接 """
        try:  
            self.driver = GraphDatabase.driver(uri, auth=(username, password))  
            # 测试连接  
            with self.driver.session() as session:  
                session.run("RETURN 1")  
            print(f"✓ 成功连接到Neo4j数据库: {uri}")  
        except Exception as e:  
            print(f"✗ 连接Neo4j失败: {e}")  
            sys.exit(1)  
      
    def close(self):  
        """关闭数据库连接"""  
        if self.driver:  
            self.driver.close()  
      
    def clear_database(self):  
        """清空数据库（可选）"""  
        with self.driver.session() as session:  
            result = session.run("MATCH (n) RETURN count(n) as count")  
            count = result.single()["count"]  
              
            if count > 0:  
                confirm = input(f"数据库中有 {count} 个节点，是否清空？(y/N): ")  
                if confirm.lower() == 'y':  
                    session.run("MATCH (n) DETACH DELETE n")  
                    print("✓ 数据库已清空")  
                else:  
                    print("保留现有数据")  
            else:  
                print("数据库为空")  
      
    def create_constraints(self):  
        """创建约束和索引以提高性能"""  
        with self.driver.session() as session:  
            try:  
                # 为实体名称创建唯一约束  
                session.run("CREATE CONSTRAINT entity_name IF NOT EXISTS FOR (e:Entity) REQUIRE e.name IS UNIQUE")  
                print("✓ 创建实体名称唯一约束")  
            except Exception as e:  
                print(f"约束可能已存在: {e}")  
      
    def import_triples(self, triples_data):  
        """ 导入三元组数据，涉及 neo4j 数据结构设置
        1. 实体类型，非必须
        2. 关系类型，必须有一种类型
        3. 关系属性，无需创建，只要导入时，自动从待导入的数据中解析了到相应的关系属性，就可以在 neo4j 中自动生成这些属性，即关系属性是在 neo4j 中动态创建的；

        索引的创建是基于属性和标签产生的：
        索引  
        ├── 节点索引  
        │   ├── 基于标签 (:Entity, :Person, etc.)  
        │   └── 基于属性 (name, id, etc.)  
        └── 关系索引  
            ├── 基于关系类型 (:RELATION, :KNOWS, etc.)  
            └── 基于属性 (type, weight, etc.)  
        """
        print(f"开始导入 {len(triples_data)} 个三元组...")  
        with self.driver.session() as session:  
            # 批量导入以提高性能  
            batch_size = 1000  
            imported_count = 0  
            for i in range(0, len(triples_data), batch_size):  
                batch = triples_data[i:i + batch_size]  
                # 使用UNWIND进行批量导入  
                session.run("""  
                    UNWIND $triples AS triple  
                    MERGE (s:Entity {name: triple.subject})  
                    MERGE (o:Entity {name: triple.object})
                    MERGE (s)-[r:RELATION {  
                        type: triple.predicate,  
                        chunk: coalesce(triple.chunk, 0),  
                        inferred: coalesce(triple.inferred, false)  
                    }]->(o)  
                """, triples=batch)  
                imported_count += len(batch)  
                print(f"已导入 {imported_count}/{len(triples_data)} 个三元组")  
        print("✓ 三元组导入完成")  


    def get_statistics(self):  
        """ 获取导入后的统计信息 """
        with self.driver.session() as session:  
            # 节点数量  
            nodes_result = session.run("MATCH (n:Entity) RETURN count(n) as count")  
            nodes_count = nodes_result.single()["count"]  
              
            # 关系数量  
            edges_result = session.run("MATCH ()-[r:RELATION]->() RETURN count(r) as count")  
            edges_count = edges_result.single()["count"]  
              
            # 推理关系数量  
            inferred_result = session.run("MATCH ()-[r:RELATION]->() WHERE r.inferred = true RETURN count(r) as count")  
            inferred_count = inferred_result.single()["count"]  
              
            # 原始关系数量  
            original_count = edges_count - inferred_count  
              
            print("\n=== Neo4j数据库统计信息 ===")  
            print(f"节点数量: {nodes_count}")  
            print(f"关系总数: {edges_count}")  
            print(f"原始关系: {original_count}")  
            print(f"推理关系: {inferred_count}")  
              
            return {  
                "nodes": nodes_count,  
                "edges": edges_count,  
                "original_edges": original_count,  
                "inferred_edges": inferred_count  
            }  
  
def load_json_data(file_path):  
    """加载JSON数据文件"""  
    try:  
        with open(file_path, 'r', encoding='utf-8') as f:  
            data = json.load(f)  
        print(f"✓ 成功加载JSON文件: {file_path}")  
        return data  
    except Exception as e:  
        print(f"✗ 加载JSON文件失败: {e}")  
        sys.exit(1)  
  
def validate_triples(triples_data):  
    """验证三元组数据格式"""  
    if not isinstance(triples_data, list):  
        print("✗ JSON数据应该是一个列表")  
        return False  
      
    valid_count = 0  
    invalid_count = 0  
      
    for i, triple in enumerate(triples_data):  
        if not isinstance(triple, dict):  
            invalid_count += 1  
            continue  
              
        required_fields = ["subject", "predicate", "object"]  
        if all(field in triple for field in required_fields):  
            valid_count += 1  
        else:  
            invalid_count += 1  
            if invalid_count <= 5:  # 只显示前5个错误  
                print(f"无效三元组 #{i}: 缺少必需字段 {required_fields}")  
      
    print(f"数据验证结果: {valid_count} 个有效三元组, {invalid_count} 个无效三元组")  
      
    if invalid_count > 0:  
        confirm = input("发现无效数据，是否继续导入有效数据？(y/N): ")  
        if confirm.lower() != 'y':  
            return False  
      
    return valid_count > 0  
  
def main():  
    parser = argparse.ArgumentParser(description='将AI知识图谱JSON数据导入Neo4j数据库')  
    parser.add_argument(
        '--json', default= '/workspace/data_graph_generate_result/红楼梦/knowledge_graph.json'
        # required=True, help='JSON数据文件路径'
    )  
    parser.add_argument('--uri', default='bolt://192.168.1.6:7689', help='Neo4j数据库URI')  
    parser.add_argument('--username', default='neo4j', help='Neo4j用户名')  
    parser.add_argument(
        '--password', default='aa1230.aa2'
        # required=True, help='Neo4j密码'
    )
    parser.add_argument('--clear', action='store_true', help='导入前清空数据库')  
      
    args = parser.parse_args()  
      
    # 加载和验证数据  
    triples_data = load_json_data(args.json)  
    if not validate_triples(triples_data):  
        print("数据验证失败，退出")  
        sys.exit(1)  
      
    # 过滤有效数据  
    valid_triples = []  
    for triple in triples_data:  
        if isinstance(triple, dict) and all(field in triple for field in ["subject", "predicate", "object"]):  
            valid_triples.append(triple)  
      
    # 连接Neo4j并导入  
    importer = Neo4jImporter(args.uri, args.username, args.password)  
      
    try:  
        if args.clear:  
            importer.clear_database()  
          
        importer.create_constraints()  
        importer.import_triples(valid_triples)  
        stats = importer.get_statistics()  
          
        print("\n=== 导入完成 ===")  
        print("您可以在Neo4j Browser中使用以下查询来探索数据:")  
        print("1. 查看所有节点: MATCH (n:Entity) RETURN n LIMIT 25")  
        print("2. 查看所有关系: MATCH (s)-[r:RELATION]->(o) RETURN s.name, r.type, o.name LIMIT 25")  
        print("3. 查看推理关系: MATCH (s)-[r:RELATION]->(o) WHERE r.inferred = true RETURN s.name, r.type, o.name LIMIT 25")  
        print("4. 查看图谱概览: MATCH (s)-[r:RELATION]->(o) RETURN s, r, o LIMIT 100")  
          
    finally:  
        importer.close()  
  
if __name__ == "__main__":  
    main()