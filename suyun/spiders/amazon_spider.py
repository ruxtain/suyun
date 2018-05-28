# -*- coding: utf-8 -*-
import scrapy
import requests
import logging
from scrapy.loader import ItemLoader
from suyun.items import ProductItem, load_amazon_item

logging.basicConfig(filename='spider.log', filemode='w', level=logging.DEBUG)

RAW_HEADERS = '''authority:www.amazon.com
method:GET
path:/s/ref=nb_sb_noss?url=me%3DA2G697YVFPFSPH&field-keywords=
scheme:https
accept:text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8
accept-encoding:gzip, deflate, br
accept-language:zh-CN,zh;q=0.9,en;q=0.8,zh-TW;q=0.7
cache-control:max-age=0
cookie:aws-target-static-id=1513133687260-387039; aws-target-visitor-id=1513133687265-600747.24_13; aws-target-data=%7B%22support%22%3A%221%22%7D; AMCV_4A8581745834114C0A495E2B%40AdobeOrg=-1891778711%7CMCIDTS%7C17514%7CMCMID%7C90967545419936877164237515768660344615%7CMCOPTOUT-1513141343s%7CNONE%7CMCAID%7CNONE%7CvVersion%7C2.4.0; s_lv=1513134143699; ca=ALAAAAgBAAAKAgQCQAEAAEQ=; regStatus=pre-register; s_vn=1544669688223%26vn%3D4; aws-ubid-main=724-8700422-6427765; __utma=194891197.1685209066.1520047283.1520047283.1520047283.1; __utmz=194891197.1520047283.1.1.utmccn=(referral)|utmcsr=google.com.hk|utmcct=/|utmcmd=referral; s_nr=1524894370719-Repeat; s_vnum=1945837418662%26vn%3D5; s_dslv=1524894370721; x-wl-uid=1DO/JVQeWMb0aSc/c1/0lEP3glnjUQFZyW14Ly6VRX8eukz45q/URMG5HQRlY6LnkdZddjP9vBgE=; gsScrollPos-189=0; s_pers=%20s_ev15%3D%255B%255B%2527Google%2527%252C%25271526978258311%2527%255D%255D%7C1684744658311%3B%20s_fid%3D1A98FFB85EE95674-0B85329062FA6AD7%7C1684744997536%3B%20s_dl%3D1%7C1526980397537%3B%20gpv_page%3DFAQ%7C1526980397539%3B; lc-main=en_US; skin=noskin; s_sess=%20c_m%3Dwww.google.com.hkNatural%2520Search%3B%20s_sq%3D%3B%20s_cc%3Dtrue%3B%20s_ppvl%3DFAQ%252C62%252C62%252C948%252C1920%252C948%252C1920%252C1080%252C1%252CL%3B%20s_ppv%3DFAQ%252C100%252C62%252C1830%252C1920%252C948%252C1920%252C1080%252C1%252CL%3B; session-id=141-2699654-6580604; ubid-main=133-0367460-4188031; session-token=rPXAnhktTWf/I8z/SNr6SIdVpQbkuB8zAjuOb6Vznu73kBEk6IT9RHyE49XPbNUfYopcbjraFuCUdHrbH95/yO8sqgxICnJBnB2kta3pHKEl5CbZOtInRM85KXvtcR76I0X0Rmb40zmDN5IC1Fr8+BQPGaygLir2XCrGPKs1wVx+EpKvKt+lK02lwIgSGrpI; session-id-time=2082787201l; csm-hit=tb:88FH9Y351EK9W3ZNGYVW+s-SXXB2H366S8XPS3AV1Z7|1527219301633&adb:adblk_no
upgrade-insecure-requests:1
user-agent:Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/64.0.3282.186 Safari/537.36'''

def get_headers():
    headers = {}
    for i in RAW_HEADERS.split('\n'):
        key, value = i.split(':', 1)
        headers[key] = value
    return headers

class AmazonSpider(scrapy.Spider):
    '''
    scrape amazon store by a store link
    '''
    name = 'amazon'
    allowed_domains = ['www.amazon.com']
    custom_settings = {
        'DEFAULT_REQUEST_HEADERS': get_headers(),
    }

    def start_requests(self):
        start_urls = ['https://www.amazon.com/s/ref=nb_sb_noss?url=me%3DA2G697YVFPFSPH&field-keywords=']
        headers = get_headers()
        for url in start_urls:
            yield scrapy.Request(url=url, callback=self.parse)

    def parse(self, response):
        headers = get_headers()
        if not response.xpath('//comment()[contains(.,"Correios.DoNotSend")]'): # not busted
            for href in response.xpath("//li[@id[starts-with(.,'result')]]/div/div[3]/div[1]/a/@href"):
                yield response.follow(href, self.parse_product)

            # 没有设定遇到验证码重试；
            next_page = response.xpath('//*[@id="pagnNextLink"]/@href').extract_first()
            if next_page:
                yield  response.follow(next_page, callback=self.parse)
        else:
            logging.info('*** BUSTED! ***')
            yield scrapy.Request(
                url=response.url, 
                headers=headers, 
                dont_filter=True, # enable loop request until parsing is successful
                callback=self.parse)

    def parse_product(self, response):
        headers = get_headers()
        if not response.xpath('//comment()[contains(.,"Correios.DoNotSend")]'): # not busted
            loader = ItemLoader(item=ProductItem(), response=response)
            item = load_amazon_item(loader)
            logging.info('*** RETURN ITEM: ***')   
            yield item            
        else:
            logging.info('*** BUSTED! ***')
            yield scrapy.Request(
                url=response.url, 
                headers=headers, 
                dont_filter=True, # enable loop request until parsing is successful
                callback=self.parse_product)
