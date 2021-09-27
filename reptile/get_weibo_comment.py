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


def get_weibo_commenr(weibo_id):
    params = {
        'id': weibo_id,
        'mid': weibo_id,
        'max_id_type': 0
    }
    url = comment_base_url + urlencode(params)
    response = requests.get(url, headers=tools.get_random_ua())
    comments = response.json()['data']['data']
    for comment in comments:
        print(pq(comment.get('text')).text())


get_weibo_commenr('4684280054415368')
