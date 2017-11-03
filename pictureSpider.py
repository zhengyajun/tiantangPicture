# /-*- coding:utf-8 -*-/

from setting import *          # 引入配置文件参数
import requests
from multiprocessing import Process, Pool
import gevent
import time
import re
from bs4 import BeautifulSoup
import logging
import os, os.path


# def get_proxy():
#     """从ip代理池中获取IP（github: Geymey / ProxyPool）"""
#     try:
#         response = requests.get(PROXY_POOL_URL)
#         if response.status_code == requests.codes.ok:
#             return response.text
#
#     except ConnectionError:
#         return None

def get_index_html():
    """获取索引页url和索引页页面，返回索引页html"""
    print('get_index_html')

    """获取索引页url"""
    global COMMON_URL
    for i in range(END_PAGE_NUM+1):
        if i == 0:
            index_url = COMMON_URL + '/tupian/index.html'
        else:
            index_keywords = COMMON_URL + '/tupian/index_' + str(i) + '.html'
            index_url = COMMON_URL + index_keywords

        """获取索引页的页面"""
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


def parse_index_html():
    """解析索引页，获取详情页的url，返回详情的页面html"""
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

                """利用关键字构造成详情页图片，返回详情页"""
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


def parse_detail_html():
    """解析详情页，获取图片链接，访问图片并保存"""
    print('parse_detail_html')
    detail_htmls = parse_index_html()

    for detail_html in detail_htmls:
        if detail_html:
            soup = BeautifulSoup(detail_html,'lxml')
            # picture_url_list = soup.select('body > div:nth-of-type(3) > div.left > ul > li:nth-of-type(1) > div > a > img')
            picture_folder = soup.select('body > div:nth-of-type(3) > div.album > div.al_tit > h1')[0].text
            print('正在创建：' + picture_folder)    # 获取当前图集标题
            pwd = mkdir(picture_folder)

            picture_url_list = soup.select('body > div:nth-of-type(3) > div.left > ul > li')

            i = 1   # 用于区分文件内图片名字
            for each in picture_url_list:
                # print(each)
                small_picture_urls = each.select('> div > a > img')[0]['src']
                picture_url = re.sub(r'tupian/(.*?)/', 'tupian/pre/', small_picture_urls)    # 将获取的缩略图放大

                """保存图片"""
                try:
                    picture = requests.get(picture_url).content
                    file_name = pwd + '/' + str(i) + '.jpg'
                    with open(file_name, 'wb') as p:               # 存入文件中
                        p.write(picture)
                        p.close()
                    print(picture_url + ' was saved!')
                    i += 1
                except:
                    print('error')

def mkdir(child_folder):
    root_path = './pictures'
    child_path = root_path + '/' + child_folder
    isExists = os.path.exists(child_path)

    if not isExists:
        os.makedirs(child_path)
        print(child_path + '创建成功')
    else:
        print(child_path + '已存在')

    return child_path

def main():
    parse_detail_html()

if __name__ == "__main__":
    main()

