# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://doc.scrapy.org/en/latest/topics/item-pipeline.html

import pymongo
import logging

# 20180526 为什么一切设置好了，pipline 不执行？
# 因为我误改 spider.py 中 yield item 为 return item
# 以为只有一个对象就没有必要 yield。这是不行的。
# spider 一律用 yield 传参。

class SuyunPipeline(object):

    collection_name = 'scrapy_items'

    def __init__(self, mongo_uri, mongo_db):
        self.mongo_uri = mongo_uri
        self.mongo_db = mongo_db

    @classmethod
    def from_crawler(cls, crawler):
        return cls(
            mongo_uri=crawler.settings.get('MONGO_URI'),
            mongo_db=crawler.settings.get('MONGO_DATABASE', 'suyun')
        )

    def open_spider(self, spider):
        self.client = pymongo.MongoClient(self.mongo_uri)
        self.db = self.client[self.mongo_db]

    def close_spider(self, spider):
        self.client.close()

    def process_item(self, item, spider):
        logging.info('*** SAVING ITEM TO MONGO: ***')
        logging.info(item)

        item = dict(item)

        # update if already exists, insert if not
        if self.db[self.collection_name].find_one({'asin':item['asin']}):
            self.db[self.collection_name].update_one({'asin':item['asin']}, {'$set': item})
            logging.info("*** UPDATED ***")
        else:
            self.db[self.collection_name].insert_one(item)
            logging.info("*** INSERTED ***")
        return item

