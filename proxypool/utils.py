# -*- coding: utf-8 -*-
import requests
from requests.exceptions import ConnectionError
from proxypool.config import USER_AGENTS
import random


def get_page(url):
    headers = {
        'User-Agent': random.choice(USER_AGENTS),
        'Accept-Encoding': 'gzip, deflate, br',
        'Accept-Language': 'zh-CN,zh;q=0.8',
        'Upgrade-Insecure-Requests': '1'
    }
    try:
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            return response.text
    except ConnectionError:
        print('爬取网页失败', url)
        return None
