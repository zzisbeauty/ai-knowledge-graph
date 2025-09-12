#!/bin/bash
set -e

CONTAINER_NAME="ai-knowledge-graph"
IMAGE_ID="d75384ce7377"
API_PORT="5620"
PROJECT_PATH="/home/nvidia/Desktop/ai-knowledge-graph"
NEO4J_CONTAINER="neo4j2"
NEO4J_HOST="neo4j2"
NEO4J_PASSWD="aa1230.aa2"
NEO4J_BOLT_PORT="7687"

echo ">>> 检查 ${NEO4J_CONTAINER} 所在的网络..."
NET_NAME=$(docker inspect -f '{{range $k,$v := .NetworkSettings.Networks}}{{println $k}}{{end}}' ${NEO4J_CONTAINER} | head -n1)
if [ -z "$NET_NAME" ]; then
  echo "未找到 ${NEO4J_CONTAINER} 的网络，请确认容器是否运行中。"
  exit 1
fi
echo "Neo4j 容器 ${NEO4J_CONTAINER} 所在网络: ${NET_NAME}"

echo ">>> 删除旧容器（如果存在）..."
docker rm -f ${CONTAINER_NAME} >/dev/null 2>&1 || true

echo ">>> 启动新容器 ${CONTAINER_NAME} ..."
docker run -d \
  --name ${CONTAINER_NAME} \
  --network ${NET_NAME} \
  -p ${API_PORT}:5620 \
  -v ${PROJECT_PATH}:/app \
  -e NEO4J_URI=bolt://${NEO4J_HOST}:${NEO4J_BOLT_PORT} \
  -e NEO4J_USER=neo4j \
  -e NEO4J_PASSWORD=${NEO4J_PASSWD} \
  ${IMAGE_ID} \
  tail -f /dev/null

echo ">>> 容器 ${CONTAINER_NAME} 已启动（后台常驻）"
echo "API 地址: http://localhost:${API_PORT}"
echo "Neo4j 地址: bolt://${NEO4J_HOST}:${NEO4J_BOLT_PORT} (容器内访问)"
