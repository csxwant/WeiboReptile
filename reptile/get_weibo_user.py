import requests
from static import tools
from time import sleep
import os.path
import threading
import random

root_path = r'E:\weibo'
# 存储微博用户ID（节点）文件
userNodes_path = r'E:\weibo\userNodes.txt'
# 存储微博用户属性文件地址
userNodes_features_1 = 'E:\\weibo\\%s.txt' % 'userNodes_features_1'
userNodes_features_2 = 'E:\\weibo\\%s.txt' % 'userNodes_features_2'
# 存储微博用户关系边文件地址
user2user_edges_path_1 = r'E:\weibo\user2user_edges_path_1.txt'
user2user_edges_path_2 = r'E:\weibo\user2user_edges_path_2.txt'
# 临时为多线程存储用户ID
user_node_l1 = []
user_node_l2 = []


def modify_file():
    """
    整理文件
    :return:
    """
    if os.path.exists(root_path) is False:
        os.mkdir(root_path)
    if os.path.exists(userNodes_path):
        os.remove(userNodes_path)
    if os.path.exists(userNodes_features_1):
        os.remove(userNodes_features_1)
    if os.path.exists(userNodes_features_2):
        os.remove(userNodes_features_2)
    if os.path.exists(user2user_edges_path_1):
        os.remove(user2user_edges_path_1)
    if os.path.exists(user2user_edges_path_2):
        os.remove(user2user_edges_path_2)


def get_specific_user_followers(ego_id):
    """
    获取特定用户的关注用户列表
    :param user_id: 特定用户ID
    :return:
    """
    # 关注爬取地址
    user_followers_url = "https://m.weibo.cn/api/container/getIndex?containerid=231051_-_followers_-_%s" % ego_id
    followers = reptile_user_followers(user_followers_url, ego_id)
    return followers


def get_specific_user_fans(ego_id):
    """
    获取特定用户的粉丝用户列表
    :param user_id: 特定用户ID
    :return:
    """
    # 粉丝爬取地址
    user_fans_url = "https://m.weibo.cn/api/container/getIndex?containerid=231051_-_fans_-_%s" % ego_id
    fans = reptile_user_fans(user_fans_url, ego_id)
    return fans


def reptile_user_followers(user_follower_url, ego_id):
    # 存储关注用户的ID
    followers = []
    try:
        # 使用随机用户代理访问并获取网页返回资源
        res = requests.get(user_follower_url, headers=tools.get_random_ua())
        # 获取相应标签
        cards = res.json()['data']['cards']
        len_cards = len(cards)
        # 关注者信息一般处于cards的最后一个标签
        cards = cards[len_cards - 1]
        # 获取用户节点文件流
        f_user_feature = open(userNodes_features_1, 'a+', encoding='utf-8')
        # 获取用户与用户关系边文件流
        f_user2user = open(user2user_edges_path_1, 'a+', encoding='utf-8')
        card_group = cards['card_group']
        # 计数器，每个用户只爬取4-6个
        num = 1
        ran_num = random.randint(4, 6)
        for card_group_info in card_group:
            try:
                user_info = card_group_info['user']
                # 该用户关注的用户的属性
                user_name = user_info['screen_name']  # 用户名
                user_id = user_info['id']  # 用户id
                if user_id <= 10:
                    print(user_id)
                fans_count = user_info['followers_count']  # 粉丝数量
                if user_info['gender'] == 'f':
                    sex = '女'
                else:
                    sex = '男'
                # 生成关注者属性字典
                info = {
                    "id": user_id,
                    "用户名": user_name,
                    "性别": sex,
                    "粉丝数": fans_count,
                }
                followers.append(user_id)
                user_node_l1.append(user_id)
                # 向边文件中写入用户关系边，格式为 a--关注-->b
                f_user2user.write(str(ego_id) + ' ' + str(user_id) + '\n')
                # 写入属性
                f_user_feature.write(str(info) + '\n')
                num += 1
            except Exception as e3:
                print('e3 error' + str(e3.args))
            if num > ran_num:
                break
        # print("%s关注信息爬取完毕..." % ego_id)
    except Exception as e1:
        print('e1 error' + str(e1.args))
    finally:
        try:
            f_user2user.close()
            f_user_feature.close()
        except Exception as e4:
            print('e4:' + str(e4.args))
    return followers


def reptile_user_fans(user_fans_url, ego_id):
    fans = []
    try:
        # 使用随机用户代理访问并获取网页返回资源
        res = requests.get(user_fans_url, headers=tools.get_random_ua(), timeout=random.randint(3, 5))
        # 获取相应标签
        cards = res.json()['data']['cards']
        # 打开结点文件与边文件准备写入
        f_user2user = open(user2user_edges_path_2, 'a+', encoding='utf-8')
        f_user_feature = open(userNodes_features_2, 'a+', encoding='utf-8')
        # 计数器，每个用户只爬取4-6个
        num = 1
        ran_num = random.randint(4, 6)
        for card in cards:
            try:
                card_group = card['card_group']
                for card_group_info in card_group:
                    try:
                        if card_group_info['card_type'] != 10:
                            continue
                        user_info = card_group_info['user']
                        # 该用户关注的用户的属性
                        user_name = user_info['screen_name']  # 用户名
                        user_id = user_info['id']  # 用户id
                        if user_id <= 10:
                            print(user_id)
                        fans_count = user_info['followers_count']  # 粉丝数量 "follow_count"为关注数
                        if user_info['gender'] == 'f':
                            sex = '女'
                        else:
                            sex = '男'
                        # 生成关注者属性字典
                        info = {
                            "id": user_id,
                            "用户名": user_name,
                            "性别": sex,
                            "粉丝数": fans_count,
                        }
                        fans.append(user_id)
                        user_node_l2.append(user_id)
                        # 将用户属性写入文件
                        f_user_feature.write(str(info) + '\n')
                        # 将用户与粉丝之间的关系边写入文件 ，形式为 a--关注-->b
                        f_user2user.write(str(user_id) + ' ' + str(ego_id) + '\n')
                        num += 1
                        if num > ran_num:
                            break
                    except Exception as e162:
                        print('P163:' + str(e162.args) + ',' + str(card_group_info))
                        print(card_group)
            except Exception as e6:
                print('e6:' + str(e6.args))
            if num > ran_num:
                break
        # print("%s粉丝信息爬取完毕..." % ego_id)
        if num < 4:
            print("%s粉丝只能爬取%d位" % (ego_id, num))
    except Exception as e5:
        print('e5:' + str(e5.args))
    finally:
        try:
            f_user2user.close()
            f_user_feature.close()
        except Exception as e7:
            print('e7:' + str(e7.args))
    return fans


def reptile_user_info(ego_id):
    print()


def get_user_sex(user_id):
    """
    获取用户性别信息
    :param user_id:
    :return:
    """
    uid_str = "230283" + str(user_id)
    # 爬取的网址前缀
    user_sex_url = "https://m.weibo.cn/api/container/getIndex?containerid={}_-_INFO&" \
                   "title=%E5%9F%BA%E6%9C%AC%E8%B5%84%E6%96%99&luicode=10000011&lfid={}" \
                   "&featurecode=10000326".format(uid_str, uid_str)
    # 必要的参数数据
    parameter_data = {
        "containerid": "{}_-_INFO".format(uid_str),
        "title": "基本资料",
        "luicode": 10000011,
        "lfid": int(uid_str),
        "featurecode": 10000326
    }
    sex = '未知'
    try:
        res = requests.get(user_sex_url, headers=tools.get_random_ua(), data=parameter_data)
        data = res.json()['data']['cards'][1]
        if data['card_group'][0]['desc'] == '个人信息':
            sex = data['card_group'][1]['item_content']
        else:
            sex = "男"
    except Exception as e2:
        print('e2 error:' + str(e2.args))
    finally:
        return sex


# 线程计数器
thread_stop_flag = 0


# 多线程爬取
class MyThread (threading.Thread):
    """
    自定义爬取线程类
    """
    def __init__(self, thread_id, id_list):
        """
        初始化线程类
        :param thread_id: 线程id
        :param id_list: 用户列表
        """
        threading.Thread.__init__(self)
        self.thread_id = thread_id
        self.id_list = id_list
        self.followers_list = []
        self.fans_list = []

    def run(self):
        print('线程%d爬取开始' % self.thread_id)
        for Id in self.id_list:
            self.followers_list = get_specific_user_followers(Id)
            self.fans_list = get_specific_user_fans(Id)
            sleep(random.randint(1, 3))
        # 线程爬取完成后，线程计数器+1
        global thread_stop_flag
        thread_stop_flag = thread_stop_flag+1
        print('线程%d爬取结束，线程完成%d' % (self.thread_id, thread_stop_flag))

    def get_followers_list(self):
        return self.followers_list

    def get_fans_list(self):
        return self.fans_list


def n_thread_reptile(followers_list, fans_list):
    r_followers_list = []
    r_fans_list = []
    thread1 = MyThread(1, followers_list)
    thread2 = MyThread(2, fans_list)
    thread1.start()
    thread2.start()
    Threads = [thread1, thread2]
    # 线程未全部结束时不执行后续
    for thread in Threads:
        thread.join()
        r_fans_list.extend(thread.get_fans_list())
        r_followers_list.extend(thread.get_followers_list())
    return r_followers_list, r_fans_list


if __name__ == '__main__':
    modify_file()
    # 爬取3186648257的关注圈与粉丝圈
    init_fans_list = get_specific_user_fans('3186648257')
    init_followers_list = get_specific_user_followers('3186648257')
    sec_followers_list, sec_fans_list = n_thread_reptile(init_followers_list, init_fans_list)
    for i in range(1, 5):
        print('第%d次循环爬取开始' % i)
        sec_followers_list, sec_fans_list = n_thread_reptile(sec_followers_list, sec_fans_list)
    # 合并用户列表
    user_node_l1 = user_node_l1 + user_node_l2
    user_node_l1.append('3186648257')
    # 去除重复用户Id
    user_node = list(set(user_node_l1))
    print(len(user_node))
    try:
        f_user_node = open(userNodes_path, 'a+', encoding='UTF-8')
        # 将用户id写入结点文件
        for user in user_node:
            f_user_node.write(str(user) + '\n')
        f_user_node.close()
    except Exception as e274:
        print('e274:' + str(e274.args))
