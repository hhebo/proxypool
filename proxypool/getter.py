# -*- coding: utf-8 -*-

import re
import time
import requests
import json
from urllib.parse import urlencode
from pyquery import PyQuery as pq
from proxypool.utils import get_page


class ProxyMetaClass(type):
    def __new__(cls, name, bases, attrs):
        count = 0
        attrs['__CrawlFunc__'] = []
        for k, v in attrs.items():
            if 'crawl_' in k:
                attrs['__CrawlFunc__'].append(k)
                count += 1
        attrs['__CrawlFuncCount__'] = count
        return type.__new__(cls, name, bases, attrs)


class FreeProxyGetter(object, metaclass=ProxyMetaClass):
    def get_raw_proxies(self, callback):
        proxies = []
        for proxy in eval("self.{}()".format(callback)):
            proxies.append(proxy)
        return proxies

    def crawl_kuaidaili(self):
        for page in range(1, 4):
            url = 'https://www.kuaidaili.com/free/inha/{}/'.format(page)
            html = get_page(url)
            ip_address = re.compile(
                '<td data-title="IP">(.*)</td>\s*<td data-title="PORT">(\w+)</td>'
            )
            re_ip_address = ip_address.findall(html)
            for address, port in re_ip_address:
                result = address + ':' + port
                yield result.replace(' ', '')
            time.sleep(2)

    def crawl_xicidaili(self):
        for page in range(1, 4):
            url = 'http://www.xicidaili.com/wt/{}'.format(page)
            html = get_page(url)
            ip_address = re.compile(
                '<td class="country"><img src="http://fs.xicidaili.com/images/flag/cn.png" alt="Cn" /></td>\s*<td>(.*?)</td>\s*<td>(.*?)</td>'
            )
            re_ip_address = ip_address.findall(html)
            for address, port in re_ip_address:
                result = address + ':' + port
                yield result.replace(' ', '')

    def crawl_daili66(self):
        for page in range(1, 4):
            url = 'http://www.66ip.cn/{}.html'.format(page)
            html = get_page(url)
            if html:
                doc = pq(html)
                trs = doc('.containerbox table tr:gt(0)').items()
                for tr in trs:
                    ip = tr.find('td:nth-child(1)').text()
                    port = tr.find('td:nth-child(2)').text()
                    yield ':'.join([ip, port])
            time.sleep(2)

    def crawl_data5u(self):
        for keyword in ['gngn', 'gnpt']:
            url = 'http://www.data5u.com/free/{}/index.shtml'.format(keyword)
            html = get_page(url)
            ip_address = re.compile(
                '<ul class="l2">\s*<span><li>(.*?)</li></span>\s*<span style="width: 100px;"><li class=".*">(.*?)</li></span>'
            )
            re_ip_address = ip_address.findall(html)
            for address, port in re_ip_address:
                result = address + ':' + port
                yield result.replace(' ', '')

    def crawl_xdaili(self):
        data = {
            'page': 1,
            'rows': 10
        }
        url = 'http://www.xdaili.cn/ipagent//freeip/getFreeIps?' + urlencode(data)
        html = get_page(url)
        html = json.loads(html)
        ip_address = html.get('RESULT')['rows']
        for address in ip_address:
            result = address['ip'] + ':' + address['port']
            yield result.replace(' ', '')
