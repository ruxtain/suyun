import scrapy
from scrapy.crawler import CrawlerProcess
from spiders.amazon_spider import AmazonSpider
from scrapy.settings import Settings

import sys

sys.path.append('../suyun')

process = CrawlerProcess(Settings())
process.crawl(AmazonSpider)
process.start() # the script will block here until the crawling is finished