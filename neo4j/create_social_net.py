from py2neo import Node, Relationship, NodeMatcher, Graph, Subgraph, RelationshipMatcher
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
import time
import json

# 各个数据集文件的位置
node_user_file = r'E:\weibo\node.txt'
node_weibo_file = r'E:\weibo\node_weibo.txt'
edges_user2user_file_1 = r'E:\weibo\edges_1.txt'
edges_user2user_file_2 = r'E:\weibo\edges_2.txt'
edges_user2weibo_file_1 = r'E:\weibo\egdes_user_to_weibo_1.txt'
edges_user2weibo_file_2 = r'E:\weibo\egdes_user_to_weibo_2.txt'
edges_user2weibo_file_3 = r'E:\weibo\egdes_user_to_weibo_3.txt'
node_user_feature_file_1 = r'E:\weibo\nodes_features_1.txt'
node_user_feature_file_2 = r'E:\weibo\nodes_features_2.txt'
node_weibo_content_file_1 = r'E:\weibo\weibo_content_1.txt'
node_weibo_content_file_2 = r'E:\weibo\weibo_content_2.txt'
node_weibo_content_file_3 = r'E:\weibo\weibo_content_3.txt'
