# coding=utf-8
# author=XingLong Pan
# date=2016-11-07

import random
import requests
import configparser
import constants
from login import CookiesHelper
from page_parser import MovieParser
from utils import Utils
from storage import DbHelper
from requests.adapters import HTTPAdapter


def init():
    config = configparser.ConfigParser()
    config.read('config.ini')
    user = config['douban']['user'],
    password = config['douban']['password']

    cookie_helper = CookiesHelper.CookiesHelper(
        user,
        password
    )
    # cookies=''
    cookies = cookie_helper.get_cookies()
    #print(cookies)

    # 读取抓取配置
    start_id = int(config['common']['start_id'])
    end_id = int(config['common']['end_id'])

    # 读取配置文件信息
    user = config['douban']['user'],
    password = config['douban']['password']

    return cookies, start_id, end_id, user, password


def run():
    cookies, start_id, end_id, user, password = init()

    # 获取模拟登录后的cookies
    cookie_helper = CookiesHelper.CookiesHelper(
        user,
        password
    )
    # cookies={}
    cookies = cookie_helper.get_cookies()
    #print(cookies)

    # 实例化爬虫类和数据库连接工具类
    movie_parser = MovieParser.MovieParser()
    db_helper = DbHelper.DbHelper()

    s = requests.Session()
    s.mount('http://', HTTPAdapter(max_retries=3))
    s.mount('https://', HTTPAdapter(max_retries=3))
    # 通过ID进行遍历
    for i in range(start_id, end_id):

        print('id: ' + str(i)+'，开始下载')
        headers = {'User-Agent': random.choice(constants.USER_AGENT)}
        try:
            # 获取豆瓣页面(API)数据
            r = s.get(
                constants.URL_PREFIX + str(i),
                headers=headers,
                cookies=cookies,
                timeout=5
            )
            r.encoding = 'utf-8'
            print('下载成功')
            # 提示当前到达的id(log)
        

            # 提取豆瓣数据
            movie_parser.set_html_doc(r.text)
            movie = movie_parser.extract_movie_info()
            print('提取数据成功')

            # 如果获取的数据为空，延时以减轻对目标服务器的压力,并跳过。
            if not movie:
                print('id: ' + str(i)+'，无效')
                Utils.Utils.delay(constants.DELAY_MIN_SECOND, constants.DELAY_MAX_SECOND)
                continue

            # 豆瓣数据有效，写入数据库
            movie['douban_id'] = str(i)
            if movie:
                print('id: ' + str(i)+'，数据保存成功')
                db_helper.insert_movie(movie)

            Utils.Utils.delay(constants.DELAY_MIN_SECOND, constants.DELAY_MAX_SECOND)
        except requests.exceptions.RequestException as e:
            print('请求超时')
            print(e)

    # 释放资源
    db_helper.close_db()


if __name__ == '__main__':
    print("开始抓取\n")
    run()
