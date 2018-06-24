# -*- coding: utf-8 -*-

# Define here the models for your spider middleware
#
# See documentation in:
# https://doc.scrapy.org/en/latest/topics/spider-middleware.html

from scrapy import signals
import requests
import random

class ProxiesMiddleware(object):
    def __init__(self, settings):
        pass

    @classmethod
    def from_crawler(cls, crawler):
        return cls(crawler.settings)

    def process_request(self, request, spider):
        # 通过一个开源项目获取 proxy
        proxy = requests.get('http://127.0.0.1:5001', timeout=1).text
        print('*** USING PROXY: ***', proxy)
        request.meta['proxy'] = "http://" + proxy

class UserAgentMiddleware(object):
    def __init__(self, settings):
        pass

    @classmethod
    def from_crawler(cls, crawler):
        cls.settings = crawler.settings # create a class attribute
        return cls(crawler.settings)

    def process_request(self, request, spider):
        user_agents = self.__class__.settings.get('USER_AGENTS') # cls.settings attribute,
        user_agent = random.choice(user_agents)
        request.headers.setdefault('User-Agent', user_agent)
        print('*** USING USER AGENT: {} ***'.format(user_agent))
