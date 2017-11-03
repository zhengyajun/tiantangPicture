# /-*- coding:utf-8 -*-/


import requests
from multiprocessing import Process, Pool
import gevent
import time
import re
from bs4 import BeautifulSoup
import logging
import os, os.path

PROXY_POOL_URL = 'http://localhost:5000/get'
PROXY_IP = None
COMMON_URL = 'http://www.ivsky.com'     # 共有的url部分
END_PAGE_NUM = 10                   # 要抓取的页数
STAER_PAGE_NUM = 0
SWITCH_IP_TIME = 10
HEADERS = {
    'User-Agent':'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/61.0.3163.100 Safari/537.36'
}
COOKIES = {
    'Cookie' : 'UM_distinctid=15f76bd4f901e6-0014b4468a4cba-3e63430c-100200-15f76bd4f9225e; statistics_clientid=me; BDTUJIAID=02452b44a40a9e21ccb5a0544eccf8c1; arccount43279=c; CNZZDATA87348=cnzz_eid%3D354657808-1509523986-null%26ntime%3D1509605000; CNZZDATA1629164=cnzz_eid%3D512641877-1509524947-null%26ntime%3D1509606068; Hm_lvt_862071acf8e9faf43a13fd4ea795ff8c=1509525639,1509590397; Hm_lpvt_862071acf8e9faf43a13fd4ea795ff8c=1509606732'
}

# def get_proxy():
#     """从ip代理池中获取IP（github: Geymey / ProxyPool）"""
#     try:
#         response = requests.get(PROXY_POOL_URL)
#         if response.status_code == requests.codes.ok:
#             return response.text
#
#     except ConnectionError:
#         return None

def start_index_urls(start, end):
    """获取索引页urls，构建索引页生成器"""
    global COMMON_URL
    for i in range(END_PAGE_NUM+1):
        if i == 0:
            index_url = COMMON_URL + '/tupian/index.html'
            yield index_url
        else:
            index_keywords = COMMON_URL + '/tupian/index_' + str(i) + '.html'
            index_url = COMMON_URL + index_keywords
            yield index_url         # 返回索引页url的生成器

def get_index_html():
    """解析索引页"""
    print('get_index_html')
    index_urls = start_index_urls(start=STAER_PAGE_NUM, end=END_PAGE_NUM)

    for index_url in index_urls:
        time.sleep(1)
        try:
            response = requests.get(index_url, headers=HEADERS, cookies=COOKIES)
            if response.status_code == requests.codes.ok:
                # return response.text
                yield response.text
            elif response.status_code == 302:
                try:
                    """云打码，超时raise timeouterror"""
                except:
                    """切换ip"""
                else:
                    """执行验证码之后的操作"""
        except:
            # return None
            yield None

def get_detail_html():
    """利用关键字构造成详情页图片，返回详情页"""
    print('get_detail_html')
    detail_urls = parse_index_html()
    for detail_url in detail_urls:
        time.sleep(1)
        try:
            response = requests.get(detail_url, headers=HEADERS, cookies=COOKIES)
            if response.status_code == 200:
                # return response.text
                yield response.text
            elif response.status_code ==302:
                pass
        except:
            # return None
            yield None

def parse_index_html():
    """解析索引页，获取详情页的url，构建详情页生成器"""
    print('parse_index_html')
    index_htmls = get_index_html()

    for index_html in index_htmls:
        if index_html:
            soup = BeautifulSoup(index_html, 'lxml')
            # detail_keywords_list = soup.select('body > div:nth-child(3) > div.left > ul > li:nth-child(1) > div > a')
            detail_keywords_list = soup.select('body > div:nth-of-type(3) > div.left > ul > li')

            for each in detail_keywords_list:
                detail_keywords = each.select('div > a')[0]['href']
                detail_url = COMMON_URL + detail_keywords
                yield detail_url              # 返回详情页请求链接的url生成器


def parse_detail_html():
    """解析详情页，获取图片链接，返回图片链接"""
    print('parse_detail_html')
    detail_htmls = get_detail_html()

    for detail_html in detail_htmls:
        if detail_html:
            soup = BeautifulSoup(detail_html,'lxml')
            # picture_url_list = soup.select('body > div:nth-of-type(3) > div.left > ul > li:nth-of-type(1) > div > a > img')
            # picture_folder = soup.select('body > div:nth-of-type(3) > div.album > div.al_tit > h1')[0].text
            # print(picture_folder)    # 获取当前图集标题
            picture_url_list = soup.select('body > div:nth-of-type(3) > div.left > ul > li')
            for each in picture_url_list:
                # print(each)
                small_picture_urls = each.select('> div > a > img')[0]['src']
                picture_urls = re.sub(r'tupian/(.*?)/', 'tupian/pre/', small_picture_urls)    # 将获取的缩略图放大
                yield picture_urls

def mkdir():
    _path = './pictures'
    isExists = os.path.exists(_path)
    if not isExists:
        os.mkdir(_path)
        print(_path + '创建成功')
    else:
        print(_path + '已存在')


def get_picture():
    """获取图片,创建相应的文件夹并保存图片"""
    print('get_picture')  # 测试
    picture_urls = parse_detail_html()
    mkdir()
    i = 1
    for picture_url in picture_urls:
        pass
        try:
            picture = requests.get(picture_url).content
            file_name = './pictures/' + str(i) + '.jpg'
            with open(file_name, 'wb') as p:               # 存入文件中
                p.write(picture)
                p.close()
            print(picture_url + ' was saved!')
            i += 1
        except:
            print('error')

if __name__ == "__main__":
    get_picture()

