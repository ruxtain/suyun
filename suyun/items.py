# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://doc.scrapy.org/en/latest/topics/items.html

import scrapy
import re
import html
from bs4 import BeautifulSoup
from scrapy.loader.processors import TakeFirst

class ProductItem(scrapy.Item):
    '''
    the fields' order is prefered by suyun
    '''
    # https://doc.scrapy.org/en/latest/topics/media-pipeline.html#topics-media-pipeline-enabling
    image_urls = scrapy.Field() 
    images = scrapy.Field()
    # custom fields
    asin = scrapy.Field()
    link = scrapy.Field()
    price = scrapy.Field()
    title = scrapy.Field()
    date = scrapy.Field() # 上架时间
    big_rank = scrapy.Field()
    big_category = scrapy.Field()
    small_rank_1 = scrapy.Field()
    small_category_1 = scrapy.Field()
    small_rank_2 = scrapy.Field()
    small_category_2 = scrapy.Field()
    small_rank_3 = scrapy.Field()
    small_category_3 = scrapy.Field()
    review = scrapy.Field()
    star = scrapy.Field()
    fba = scrapy.Field()

def get_field_date(value):
    try:
        return value[0].strip()
    except IndexError:
        return ''

def get_field_big_rank(value):
    if len(value) > 0:
        value = re.findall(r'#([\d,]+)', value[0])[0]
        return value.replace(',', '')
    else:
        return ''

def get_field_big_category(value):
    if len(value)>0:
        return html.unescape(value[0])
    else:
        return ''

def get_field_ranks(value):
    '''
    num: the order number of the small rank, starting from 1
    '''
    if len(value) > 0:
        ranks = re.findall(r'#([\d,]+)\D', value[0])
        return ranks
    else:
        return ''

def take_second(value):
    if len(value) >= 2:
        return value[1]
    else:
        return ''

def take_thrid(value):
    if len(value) >= 3:
        return value[2]
    else:
        return ''

def take_forth(value):
    if len(value) >= 4:
        return value[3]
    else:
        return ''

def get_field_small_categories(value):
    if len(value) > 0:
        value = re.sub(r'</b>', '', value[0])
        value = re.findall(r'last">(.*?)</a></span>', value)
        return value
    else:
        return ''


def load_amazon_item(loader):
    '''
    The page structure is like this one:
    https://www.amazon.com/dp/B0799JN2Z3
    '''
    loader.add_xpath('image_urls', '//script[contains(text(), "ImageBlockATF")]/text()', TakeFirst(), re='"large":"(https://.*?\.jpg)",')
    loader.add_xpath('title', '//span[@id="productTitle"]/text()', lambda s:s[0].strip())
    loader.add_xpath('star', '//*[@id="acrPopover"]/span[1]/a/i[1]/span/text()', TakeFirst(), re='([\d.]+)\s')
    loader.add_xpath('asin', '//link[@rel="canonical"]/@href', re='dp/([A-Z\d]{10})')
    loader.add_xpath('review', '//span[@id="acrCustomerReviewText"]/text()', TakeFirst(), lambda i:i.replace(',', ''), re='[\d,]+')
    loader.add_xpath('price', '//span[@id="priceblock_ourprice"]/text()')
    loader.add_xpath('date', '//table[@id="productDetails_detailBullets_sections1"]/tr/th[contains(text(), "Date first listed on Amazon")]/following-sibling::td[1]/text()', get_field_date)
    loader.add_xpath('big_rank','//*[contains(text(), "Best Sellers Rank")]/ancestor::*[1]', get_field_ranks, TakeFirst())
    loader.add_xpath('big_category','//*[contains(text(), "Best Sellers Rank")]/ancestor::*[1]', get_field_big_category, re='#[\d,]+ [iI]n (.*?) \(<a href') # risky
    loader.add_xpath('small_rank_1','//*[contains(text(), "Best Sellers Rank")]/ancestor::*[1]', get_field_ranks, take_second)
    loader.add_xpath('small_rank_2','//*[contains(text(), "Best Sellers Rank")]/ancestor::*[1]', get_field_ranks, take_thrid)
    loader.add_xpath('small_rank_3','//*[contains(text(), "Best Sellers Rank")]/ancestor::*[1]', get_field_ranks, take_forth)
    loader.add_xpath('small_category_1','//*[contains(text(), "Best Sellers Rank")]/ancestor::*[1]', get_field_small_categories, TakeFirst())
    loader.add_xpath('small_category_2','//*[contains(text(), "Best Sellers Rank")]/ancestor::*[1]', get_field_small_categories, take_second)
    loader.add_xpath('small_category_3','//*[contains(text(), "Best Sellers Rank")]/ancestor::*[1]', get_field_small_categories, take_thrid)
    loader.add_xpath('fba', '//a[@id="SSOFpopoverLink"]/text()', lambda i:'Fulfilled by Amazon' in i)
    return loader.load_item()      

def main():
    ''' only for testing '''
    import os
    from scrapy.http import Response, Request, TextResponse
    from scrapy.loader import ItemLoader

    def fake_response_from_file(file_name, url=None):
        if not url:
            url = 'http://www.amazon-fake-requests.com'

        request = Request(url=url)
        if not file_name[0] == '/':
            responses_dir = os.path.dirname(os.path.realpath(__file__))
            file_path = os.path.join(responses_dir, file_name)
        else:
            file_path = file_name

        file_content = open(file_path, 'r', encoding='utf-8').read()

        response = TextResponse(url=url,
            request=request,
            body=file_content.encode('utf-8'))
        return response

    def item_from_file(filename, func):
        response = fake_response_from_file(filename)
        loader = ItemLoader(item=ProductItem(), response=response)
        return func(loader)

    test_list = [
        item_from_file('..\\tests\\test_detail_info_side.html', load_side_listing),
        item_from_file('..\\tests\\test_detail_new.html', load_side_listing),
        item_from_file('..\\tests\\test_detail_old.html', load_side_listing),
        item_from_file('..\\tests\\test_detail_test.html', load_side_listing),
    ]
    for i in test_list:
        print(i)
        # print(i['fba'])
        # print(i['small_category_2'])
        # print(i['small_category_3'])
        # # print(i['big_rank'])
        # # print(i['small_rank_1'])
        # # print(i['small_rank_2'])
        # # print(i['small_rank_3'])
        print('-'*80)


if __name__ == '__main__':
    main()