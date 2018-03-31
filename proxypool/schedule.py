# -*- coding: utf-8 -*-

import time
import aiohttp
import asyncio
from aiohttp import ClientConnectionError
from asyncio import TimeoutError
from multiprocessing import Process
from proxypool.db import RedisClient
from proxypool.getter import FreeProxyGetter
from proxypool.config import VALID_CHECK_CYCLE, POOL_LEN_CHECK_CYCLE, \
    POOL_LOWER_THRESHOLD, POOL_UPPER_THRESHOLD, TEST_API, get_proxy_timeout


class ValidityTester(object):
    test_api = TEST_API

    def __init__(self):
        self._raw_proxies = None
        self._usable_proxies = []

    def set_raw_proxies(self, proxies):
        self._raw_proxies = proxies
        self._conn = RedisClient()

    async def test_proxy(self, proxy):
        try:
            async with aiohttp.ClientSession() as session:
                try:
                    if isinstance(proxy, bytes):
                        proxy = proxy.decode('utf-8')
                    real_proxy = 'http://' + proxy
                    print('测试 ip', proxy)
                    async with session.get(self.test_api, proxy=real_proxy, timeout=get_proxy_timeout) as response:
                        if response.status == 200:
                            self._conn.put(proxy)
                            print('可用 ip', proxy)
                except (ClientConnectionError, TimeoutError, ValueError):
                    print('无效 ip', proxy)
        except ClientConnectionError as e:
            print(e)
            pass

    def test(self):
        print('正在测试')
        try:
            loop = asyncio.get_event_loop()
            tasks = [self.test_proxy(proxy) for proxy in self._raw_proxies]
            loop.run_until_complete(asyncio.wait(tasks))
        except ValueError:
            print('测试失败')


class PoolAdder(object):
    def __init__(self, threshold):
        self._threshold = threshold
        self._conn = RedisClient()
        self._tester = ValidityTester()
        self._crawler = FreeProxyGetter()

    def is_over_threshold(self):
        return True if self._conn.length >= self._threshold else False

    def add_to_queue(self):
        print('正在添加 ip')
        count = 0
        while not self.is_over_threshold():
            for callback_label in range(self._crawler.__CrawlFuncCount__):
                callback = self._crawler.__CrawlFunc__[callback_label]
                raw_proxies = self._crawler.get_raw_proxies(callback)
                self._tester.set_raw_proxies(raw_proxies)
                self._tester.test()
                count += len(raw_proxies)
                if self.is_over_threshold():
                    print('代理池已满')
                    break
            if count == 0:
                return None


class Schedule(object):
    @staticmethod
    def valid_proxy(cycle=VALID_CHECK_CYCLE):
        conn = RedisClient()
        tester = ValidityTester()
        while True:
            print('更新 ip 代理池')
            length = int(0.5 * conn.length)
            if length == 0:
                print('等待添加 ip')
                time.sleep(cycle)
                continue
            raw_proxies = conn.get(length)
            tester.set_raw_proxies(raw_proxies)
            tester.test()
            time.sleep(cycle)

    @staticmethod
    def check_pool(lower_threshold=POOL_LOWER_THRESHOLD,
                   upper_threshold=POOL_UPPER_THRESHOLD,
                   cycle=POOL_LEN_CHECK_CYCLE):
        conn = RedisClient()
        adder = PoolAdder(upper_threshold)
        while True:
            if conn.length < lower_threshold:
                adder = adder.add_to_queue()
            time.sleep(cycle)

    def run(self):
        print('开始运行')
        valid_process = Process(target=Schedule.valid_proxy)
        check_process = Process(target=Schedule.check_pool)
        valid_process.start()
        check_process.start()
