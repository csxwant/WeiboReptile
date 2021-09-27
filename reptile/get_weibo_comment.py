import requests
import urllib
import time
import datetime
import threading
from time import sleep
import re
from random import randint
import os
from urllib.parse import urlencode
from pyquery import PyQuery as pq
from static import tools

comment_base_url = 'https://m.weibo.cn/comments/hotflow?'


def get_weibo_comment(weibo_id, f_weibo_comments):
    params = {
        'id': weibo_id,
        'mid': weibo_id,
        'max_id_type': 0
    }
    comment_data = {
        "weibo_id": weibo_id,
        "comments_list": []
    }
    comments_list = []
    url = comment_base_url + urlencode(params)
    response = requests.get(url, headers=tools.get_random_ua())
    try:
        comments = response.json()['data']['data']
        for comment in comments:
            try:
                comment_text = pq(comment.get('text')).text()
                comments_list.append(comment_text)
            except:
                continue
        comment_data['comments_list'] = comments_list
        f_weibo_comments.write(str(comment_data) + '\n')
    except:
        pass


# get_weibo_comment('4684280054415368')
# data = {
#     'weibo_id': 1
#     }
#
# data['weibo_id'] = 2
# print(str(data))
# print(tools.get_random_ua()['User-Agent'])
