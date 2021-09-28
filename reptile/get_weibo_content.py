import requests
import time
import threading
from time import sleep
from random import randint
import os
from urllib.parse import urlencode
from pyquery import PyQuery as Pq
from static import tools
from get_weibo_comment import get_weibo_comment

# 手机端微博的网址
host = 'm.weibo.cn'
# 个人主页
base_url = 'https://%s/api/container/getIndex?' % host
# 博文
weibo_baseurl = 'https://m.weibo.cn/detail/'
# 存储地址
edges_user_pub_weibo = r'E:\weibo\edges_user_pub_weibo_%s.txt'  # 发表关系
edges_user_trans_weibo = r'E:\weibo\edges_user_trans_weibo_%s.txt'  # 转发关系
weibo_content = r'E:\weibo\weibo_content_%s.txt'
weiboNodes_path = r'E:\weibo\weiboNodes.txt'
weibo_comments_path = r'E:\weibo\weibo_comments_%s.txt'


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


def get_single_page(user_id, page=1):
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
        'User-Agent': tools.get_random_ua()['User-Agent']
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


def analysis(response_json, user_id, thread_id, weibo_id_list, f_weibo_comment):
    """
    解析爬取用户博文页面返回的json数据
    :param f_weibo_comment: 写入评论句柄
    :param response_json: 返回的json数据
    :param user_id: 爬取的用户id
    :param thread_id: 线程id
    :param weibo_id_list: 存储博文id的列表
    :return:
    """
    # 博文所处的位置
    items = response_json.get('data').get('cards')
    # 当博文大于6条时，随机爬取3到6条
    if len(items) > 6:
        num = randint(3, 6)
    # 博文数小于3条时，全部爬取
    else:
        num = len(items)
    current_num = 0
    f_user_pub_weibo = open(edges_user_pub_weibo % str(thread_id), 'a+', encoding='utf-8')
    f_user_trans_weibo = open(edges_user_trans_weibo % str(thread_id), 'a+', encoding='utf-8')
    f_weibo_content = open(weibo_content % str(thread_id), 'a+', encoding='utf-8')
    for item in items:
        try:
            init_wb = item.get('mblog')
            # 存在微博
            if init_wb:
                weibo_id = init_wb.get('id')
                cr_time = trans_format(init_wb.get('created_at'))
                # 获取本项目所需属性
                data = {
                    'weibo_id': weibo_id,
                    '发表时间': cr_time,
                    'text': Pq(init_wb.get("text")).text(),  # 仅提取内容中的文本
                    '点赞': init_wb.get('attitudes_count'),   # 点赞数
                    '评论': init_wb.get('comments_count'),    # 评论数
                    # 'reposts': init_wb.get('reposts_count')     # 转发数
                }
                # 代表是转发的微博
                if init_wb.get('retweeted_status') is not None:
                    trans_weibo = init_wb.get('retweeted_status')
                    trans_weibo_id = trans_weibo.get('id')
                    trans_weibo_created_at = trans_format(trans_weibo.get('created_at'))
                    trans_weibo_content = get_specific_weibo(trans_weibo_id)
                    trans_weibo_content = Pq(trans_weibo_content).text()
                    data['text'] = trans_weibo_content
                    data['发表时间'] = trans_weibo_created_at
                    # 博文ID暂存列表
                    weibo_id_list.append(trans_weibo_id)
                    # 写入文件
                    f_user_trans_weibo.write(str(user_id) + ' ' + str(trans_weibo_id) + '\n')
                    f_weibo_content.write(str(data) + '\n')
                    get_weibo_comment(trans_weibo_id, f_weibo_comment)
                else:
                    # 博文ID暂存列表
                    weibo_id_list.append(weibo_id)
                    # 写入文件
                    f_user_pub_weibo.write(str(user_id) + ' ' + str(weibo_id) + '\n')
                    f_weibo_content.write(str(data) + '\n')
                    get_weibo_comment(weibo_id, f_weibo_comment)
                current_num += 1
            if current_num >= num:
                break
        except Exception as e116:
            # print('e116:' + str(e116.args))
            pass
    f_user_trans_weibo.close()
    f_user_pub_weibo.close()
    f_weibo_content.close()


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
        'User-Agent': tools.get_random_ua()['User-Agent']
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


class MyThread (threading.Thread):
    """
    自定义线程，爬取内容分根据用户ID分为4个线程一起爬，加快速率
    """
    def __init__(self, thread_id, user_id_list):
        """
        初始化线程函数
        :param thread_id: 线程id
        :param user_id_list: 用户id列表
        """
        threading.Thread.__init__(self)
        self.thread_id = thread_id
        self.user_id_list = user_id_list
        self.weibo_id_list = []
        # 删除已有文件
        if os.path.exists(weibo_content % thread_id):
            os.remove(weibo_content % thread_id)
        if os.path.exists(edges_user_pub_weibo % thread_id):
            os.remove(edges_user_pub_weibo % thread_id)
        if os.path.exists(edges_user_trans_weibo % thread_id):
            os.remove(edges_user_trans_weibo % thread_id)
        if os.path.exists(weibo_comments_path % thread_id):
            os.remove(weibo_comments_path % thread_id)
        self.f_weibo_comment = open(weibo_comments_path % thread_id, 'w+', encoding='utf-8')

    def run(self):
        """
        线程函数
        :return:
        """
        print('线程%d爬取开始' % self.thread_id)
        for user_id in self.user_id_list:
            try:
                response_json = get_single_page(user_id)
                analysis(response_json, user_id, self.thread_id, self.weibo_id_list, self.f_weibo_comment)
                sleep(randint(1, 3))
            except Exception as e1:
                print(e1.args)
        # 线程计数器，爬取完加1
        global thread_countLock
        thread_countLock = thread_countLock + 1
        print('线程%d爬取结束' % self.thread_id)
        self.f_weibo_comment.close()

    def get_weibo_id_list(self):
        return self.weibo_id_list


# 线程计数器
thread_countLock = 0
user_id_list = []


def work_fun():
    try:
        f_users_id = open(r'E:\weibo\userNodes.txt', 'r', encoding='utf-8')
        lines = f_users_id.readlines()
        for line in lines:
            user_id = line.strip('\n')
            user_id_list.append(user_id)
        f_users_id.close()
        # 将用户结点列表一分为三
        each_coverage_size = int(len(user_id_list)/4)
        # 所有博文ID
        all_weibo_id_list = []
        # 开始爬取时间
        # time_start = time.time()
        # 创建线程爬取
        thread1 = MyThread(1, user_id_list[0: each_coverage_size])
        thread2 = MyThread(2, user_id_list[each_coverage_size: 2*each_coverage_size])
        thread3 = MyThread(3, user_id_list[2*each_coverage_size: 3*each_coverage_size])
        thread4 = MyThread(4, user_id_list[3 * each_coverage_size:])
        thread1.start()
        thread2.start()
        thread3.start()
        thread4.start()
        # 爬取完之前不执行后续工作
        reptile_threads = [thread1, thread2, thread3, thread4]
        for thread in reptile_threads:
            thread.join()
            all_weibo_id_list.extend(thread.get_weibo_id_list())
        # 将博文id写入文件
        all_weibo_id_list = list(set(all_weibo_id_list))
        f_weibo_id = open(weiboNodes_path, 'w+', encoding='utf-8')
        for weibo_id in all_weibo_id_list:
            f_weibo_id.write(weibo_id + '\n')
    except Exception as e:
        print('error:', e.args)
    finally:
        f_weibo_id.close()
        # time_end = time.time()
        # print('\n totally cost', time_end - time_start)  # 显示程序运行时间
