# all components will be controlled by main.py,
# multiple main.py will only make things confusing,

import sys
import time
import scrapy
import random
import logging
from scrapy.crawler import CrawlerProcess
from scrapy.utils.project import get_project_settings
from multiprocessing import Process

from suyun.spiders.amazon_spider import AmazonSpider

logging.basicConfig(filename='suyun.log', filemode='w', level=logging.DEBUG)

def spider_run():
    process = CrawlerProcess(get_project_settings())
    process.crawl(AmazonSpider)
    process.start() # the script will block here until the cırawling is finished

def run():
    p = Process(target=spider_run)
    p.start()
    p.join()

run()

# schedule.run(),

