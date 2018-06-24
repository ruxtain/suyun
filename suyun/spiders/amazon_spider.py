# -*- coding: utf-8 -*-
import scrapy
import requests
import logging
from scrapy.loader import ItemLoader
from suyun.items import ProductItem, load_amazon_item

logging.basicConfig(filename='spider-amazon.log', filemode='w', level=logging.DEBUG)

class AmazonSpider(scrapy.Spider):
    '''
    scrape amazon store by a store link
    '''
    name = 'amazon'
    allowed_domains = ['www.amazon.com']

    def start_requests(self):
        start_urls = ['https://www.amazon.com/s/ref=sr_nr_p_4_0?me=AY5XLL1NQPR7O&fst=as%3Aoff&rh=p_4%3ASUAOKI&ie=UTF8&qid=1527750475']
        for url in start_urls:
            yield scrapy.Request(url=url, callback=self.parse)

    def parse(self, response):
        if not response.xpath('//comment()[contains(.,"Correios.DoNotSend")]'): # not busted
            for href in response.xpath("//li[@id[starts-with(.,'result')]]/div/div[3]/div[1]/a/@href"):
                yield response.follow(href, self.parse_product)

            # 没有设定遇到验证码重试；
            next_page = response.xpath('//*[@id="pagnNextLink"]/@href').extract_first()
            if next_page:
                yield  response.follow(next_page, callback=self.parse)
        else:
            logging.info('*** BUSTED! ***')
            proxy = response.request.meta['proxy']
            info = requests.get('http://127.0.0.1:5001/delete/?value=' + proxy, timeout=1).text
            logging.info('*** {} ***'.format(info.upper()))
            yield scrapy.Request(
                url=response.url,
                dont_filter=True, # enable loop request until parsing is successful
                callback=self.parse)

    def parse_product(self, response):
        if not response.xpath('//comment()[contains(.,"Correios.DoNotSend")]'): # not busted
            loader = ItemLoader(item=ProductItem(), response=response)
            item = load_amazon_item(loader)
            logging.info('*** RETURN ITEM: ***')
            yield item
        else:
            logging.info('*** BUSTED! ***')
            yield scrapy.Request(
                url=response.url,
                dont_filter=True, # enable loop request until parsing is successful
                callback=self.parse_product)
