import requests
from requests.auth import HTTPBasicAuth

# 配置 Neo4j 基本信息
url = "http://10.0.15.21:7474/db/neo4j/tx/commit"   # 默认 database 为 neo4j
username = "neo4j"
password = "9NV84tLTcBLoVt"

# 写一个 Cypher 查询
query = {
    "statements": [
        {
            "statement": "MATCH (n) RETURN n LIMIT 5"
        }
    ]
}



# 发请求
response = requests.post(
    url, 
    json=query,
    auth=HTTPBasicAuth(username, password),
    headers={"Content-Type": "application/json"}
)



# 打印结果
if response.status_code == 200:
    data = response.json()
    print("查询成功！")
    print(data["results"][0]["data"])
else:
    print("请求失败:", response.status_code)
    print(response.text)

