"""
从 dify 获取数据
"""
import json
import requests
from dify_client.read_conf import *

def get_doc_split():
    api = '/chunk/list'
    # f'/datasets/{dataset_id}/documents/{doc_id}/segments'
    url = hw_dify_api_base_url + api

    kb_id = '493eddcb-0ed0-44f8-ad62-7166e078fa6a'
    doc_id = '1f12c718-9027-40a5-9dc8-a5f49695a6c4'
    data = {'kb_id': kb_id, 'doc_id': doc_id}

    text = ''
    response = json.loads(requests.get(url, params=data).text)
    datas = response['data']['chunks']
    for content in datas:
        text += content['content_with_weight']
    
    with open('now_data.txt','w',encoding='utf-8') as f:
        f.write(text)

    return text


if __name__ == "__main__":
    get_doc_split()
