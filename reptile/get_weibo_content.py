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

# 手机端微博的网址
host = 'm.weibo.cn'
# 个人主页
base_url = 'https://%s/api/container/getIndex?' % host
# 博文
weibo_baseurl = 'https://m.weibo.cn/detail/'


def trans_format(time_string, from_format="%a %b %d %H:%M:%S +0800 %Y", to_format='%Y.%m.%d %H:%M:%S'):
    """
    @note 时间格式转化
    :param time_string:
    :param from_format:
    :param to_format:
    :return:
    """
    time_struct = time.strptime(time_string, from_format)
    times = time.strftime(to_format, time_struct)
    return times


def get_single_page(page, user_id):
    """
    爬取第page页的用户博文内容
    这里为了简便分析，一般只爬取一个用户2-6条博文
    :param page:  页码
    :param user_id:  需要爬取的用户id
    :return:
    """
    # 必要的参数
    params = {
        'type': 'uid',
        'value': user_id,
        'containerid': int('107603' + user_id),  # containerid就是微博用户id前面加上107603
        'page': page
    }
    # 爬取请求头
    headers = {
        'Host': host,
        'Referer': 'https://m.weibo.cn/u/%s' % user_id,
        'User-Agent': tools.get_random_ua()
    }
    # 爬取网址
    url = base_url + urlencode(params)
    try:
        # 请求网页
        response = requests.get(url, headers=headers)
        # 请求成功
        if response.status_code == 200:
            return response.json()
    except requests.ConnectionError as e60:
        print('e60抓取错误:', e60.args)


def analysis(json, user_id, node_list):  # 保存图片的文件夹路径
    """
    解析爬取用户博文页面返回的json数据
    :param json: 返回的json数据
    :param user_id: 爬取的用户id
    :param thread_id: 线程id
    :param node_list: 存储博文id的列表
    :return:
    """
    # 博文所处的位置
    items = json.get('data').get('cards')
    # 当博文大于6条时，随机爬取3到6条
    if len(items) > 6:
        num = randint(3, 6)
    # 博文数小于3条时，全部爬取
    else:
        num = len(items)
    for item in items:
        init_wb = item.get('mblog')
        if init_wb:
            weibo_id = init_wb.get('id')
            cr_time = trans_format(init_wb.get('created_at'))
            # 获取本项目所需属性
            data = {
                'weibo_id': weibo_id,
                'created_at': cr_time,
                'text': pq(init_wb.get("text")).text(),  # 仅提取内容中的文本
                '点赞': init_wb.get('attitudes_count'),#点赞数
                '评论': init_wb.get('comments_count'),#评论数
                'reposts': init_wb.get('reposts_count')#转发数
            }
            # 获取博文内容
            text = pq(init_wb.get("text")).text()
            # 代表是转发的微博
            if init_wb.get('retweeted_status') is not None:
                trans_weibo = init_wb.get('retweeted_status')
                trans_id = trans_weibo.get('id')
                content = get_specific_weibo(trans_id)
                content = pq(content).text()
            else:
                # 博文存储列表存储该博文id
                print(text)
                # 写入文件


def get_specific_weibo(weibo_id):
    """
    爬取特定博文内容
    :param weibo_id:
    :return:
    """
    # 爬取请求头
    headers = {
        'Host': host,
        'Referer': 'https://m.weibo.cn/detail/%s' % weibo_id,
        'User-Agent': tools.get_random_ua()
    }
    # 爬取网址
    url = weibo_baseurl + weibo_id
    try:
        # 请求网页
        response = requests.get(url, headers=headers)
        # 请求成功
        if response.status_code == 200:
            text = str(response.text).split('"text": "')[1].split('"textLength"')[0].replace(' ",', '')
            return text
    except requests.ConnectionError as e:
        print('抓取错误', e.args)