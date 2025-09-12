"""Centralized repository for all LLM prompts used in the knowledge graph system."""

# Phase 1: Main extraction prompts
MAIN_SYSTEM_PROMPT = """
你是一个高级 AI 系统，专门用于知识抽取和知识图谱生成，你的专长包括识别文本中一致的实体指代和有意义的关系。
关键要求：所有关系（谓词）必须不超过 3 个单词，理想情况下为 1-2 个单词。这是一条硬性限制。
"""





# # 实体和关系抽取要求说明
# MAIN_USER_PROMPT = """
# 你的任务：
# 阅读下方以三重反引号括起来的文本，并识别每个句子中的主语-谓语-宾语（S-P-O）关系。然后输出一个JSON 数组，每个对象表示一个三元组。

# 请严格遵守以下规则：
# - 实体一致性：文档中提到的实体请使用统一名称。例如，如果“John Smith”在不同地方被称为“John”、“Mr. Smith”和“John Smith”，请在所有三元组中统一使用最完整的形式。
# - 原子化术语：请识别出明确的关键术语（如物体、地点、组织、缩写、人物、疾病、概念、情绪等）。避免将多个含义合并为一个术语，术语应尽量原子化。
# - 统一指代：如能根据原始数据的上下文逻辑正确识别代词信息，请用实体名称替换文本中的代词（如“他”、“她”、“它”、“他们”等）。
# - 成对关系抽取：如果多个术语在同一句或上下文紧密的段落中同时出现，并存在意义明确的关系，请为每一对相关术语生成一条三元组。
# - 关键要求：谓词（predicate）必须简洁，最多不超过 3 个单词（最好是 1~2 个）。这是硬性限制。
# - 请尽可能完整地抽取文本中的所有关系，并以 S-P-O 的形式表示。
# - 术语标准化：如果相同概念在文本中出现了不同的写法（如“人工智能”和“AI”），请统一为最常见或规范的形式。
# - 如果文中提到人物，请尽可能补充该人物的所在地点、职业以及知名事迹（如发明、创作、创办、头衔等），前提是这些信息在上下文中明确且适用。

# 重要说明：
# - 实体命名要尽可能精准具体，避免混淆相似但不同的概念。
# - 如果文本中有相同概念，请保持一致命名以增强三元组的连通性。
# - 提取关系时要结合上下文，避免孤立理解。
# - 所有谓词必须为不超过 3 个单词的短语（最多三个词），不得超出，这是严格要求。

# 输出要求：
# - 不得输出任何非 JSON 的文字或注释。
# - 只返回一个JSON 数组，数组中的每个对象包含 subject、predicate 和 object 三个字段。
# - 输出的 JSON 必须是有效且格式正确的。

# 输出示例结构如下：
# [
#   {
#     "subject": "Term A",
#     "predicate": "relates to",
#     "object": "Term B"
#   },
#   {
#     "subject": "Term C",
#     "predicate": "uses",
#     "object": "Term D"
#   }
# ]

# 注意：只输出 JSON 数组，不包含任何其他文本。

# 待分析的文本用三重反引号（```）包裹。
# """


MAIN_USER_PROMPT = """
您的任务：阅读下面的文本并提取所有主谓宾关系...  
  
输出要求：  
- 必须返回有效的 JSON 数组  
- 字段名必须使用英文：subject, predicate, object  
- 不要包含任何解释文字，只返回 JSON  
  
示例格式：  
[  
  {  
    "subject": "实体A",  
    "predicate": "关系",  
    "object": "实体B"  
  }  
]  
  
重要：只输出 JSON 数组，不要其他内容  
要分析的文本（三个反引号之间）：  
"""


# Phase 2: Entity standardization prompts
ENTITY_RESOLUTION_SYSTEM_PROMPT = """
你是一位实体消歧与知识表示方面的专家。
你的任务是对知识图谱中的实体名称进行标准化，以确保命名的一致性。
"""

def get_entity_resolution_user_prompt(entity_list):
    return f"""
以下是从知识图谱中提取的一组实体名称，其中部分可能指代相同的现实世界实体，但表达方式不同。

请识别出指代同一概念的实体组，并为每组提供一个标准化名称。
请将你的答案以 JSON 对象的形式返回，其中：

实体列表:
{entity_list}

请将你的回答格式化为如下所示的有效 JSON：
{{
  "standardized name 1": ["variant 1", "variant 2"],
  "standardized name 2": ["variant 3", "variant 4", "variant 5"]
}}
"""

# Phase 3: Community relationship inference prompts 社区关系推理提示语
RELATIONSHIP_INFERENCE_SYSTEM_PROMPT = """
你是一位知识表示与推理方面的专家。
你的任务是推断出知识图谱中未直接关联实体之间的可能关系。
"""

def get_relationship_inference_user_prompt(entities1, entities2, triples_text):
    return f"""
我有一个知识图谱，其中包含两个彼此不相连的实体社区。

Community 1 entities: {entities1}
Community 2 entities: {entities2}

以下是涉及这些实体的一些现有关系：
{triples_text}

请推断出社区 1 中的实体与社区 2 中的实体之间的 2-3 个可能关系。
请将你的答案以以下格式的 JSON 数组形式返回：

[
  {{
    "subject": "entity from community 1",
    "predicate": "inferred relationship",
    "object": "entity from community 2"
  }},
  ...
]

仅包含具有高度可信度的关系，并确保谓词清晰明确。
重要： 推断出的关系（谓词）最多不超过 3 个单词，理想情况下为 1-2 个单词，绝不超过 3 个单词。
对于谓词，使用简短的短语来清晰描述关系。
重要： 确保主语和宾语是不同的实体，避免自我引用。
"""

# Phase 4: Within-community relationship inference prompts - 社区内关系推理提示语
""" 推断同一社区内的潜在关系 / 推理社区内实体之间的合理联系 / 为同一社区的实体生成可能的关系 / 从同一社群中的实体中推断关系 / 推测社区内未直接连接的实体之间的关系 """
WITHIN_COMMUNITY_INFERENCE_SYSTEM_PROMPT = """
你是一位知识表示与推理方面的专家。
你的任务是推断出在知识图谱中尚未连接的语义相关实体之间的可能关系。
"""



# English
# def get_within_community_inference_user_prompt(pairs_text, triples_text):
#     return f"""
# I have a knowledge graph with several entities that appear to be semantically related but are not directly connected.

# Here are some pairs of entities that might be related:
# {pairs_text}

# Here are some existing relationships involving these entities:
# {triples_text}

# Please infer plausible relationships between these disconnected pairs.
# Return your answer as a JSON array of triples in the following format:

# [
#   {{
#     "subject": "entity1",
#     "predicate": "inferred relationship",
#     "object": "entity2"
#   }},
#   ...
# ]

# Only include highly plausible relationships with clear predicates.
# IMPORTANT: The inferred relationships (predicates) MUST be no more than 3 words maximum. Preferably 1-2 words. Never more than 3.
# IMPORTANT: Make sure that the subject and object are different entities - avoid self-references.
# """ 

# Chainese
def get_within_community_inference_user_prompt(pairs_text, triples_text):
    return f"""
我有一个知识图谱，其中有多个实体在语义上似乎存在关联，但它们之间没有直接连接。
以下是一些可能存在关联的实体对：
{pairs_text}

以下是这些实体当前已有的关系：
{triples_text}

请推理出这些未连接实体对之间可能存在的关系。
请将你的答案以 JSON 三元组数组的形式返回，格式如下：

[
  {{
    "subject": "entity1",
    "predicate": "inferred relationship",
    "object": "entity2"
  }},
  ...
]

只需返回非常可信且具有清晰谓词的关系。
重要说明：推理出的谓词（predicate）不得超过 3 个词，最好为 1 到 2 个词，绝对不能超过 3 个词。
重要说明：确保 subject 和 object 是不同的实体 —— 避免自引用。
""" 
