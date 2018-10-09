from scrapy.conf import settings
from urllib import urlencode
from scrapy import Request
from lxml import html

import scrapy
from scrapy.item import Item, Field
import re
import json


class SiteProductItem(Item):
    title = Field()
    brand = Field()
    price = Field()
    original_price = Field()
    discount_rate = Field()


class AmazonScraper (scrapy.Spider):
    name = "scrapingdata"
    allowed_domains = ['www.amazon.com']

    START_URL = 'https://amazon.com'

    settings.overrides['ROBOTSTXT_OBEY'] = False

    def __init__(self, **kwargs):
        self.product_url = kwargs['product_url']
        self.headers = {"User-Agent": "Mozilla/5.0 (X11; Linux x86_64) "
                                "AppleWebKit/537.36 (KHTML, like Gecko) "
                                "Chrome/57.0.2987.133 Safari/537.36"}

    def start_requests(self):
        yield Request(url=self.product_url,
                      callback=self.parse_page,
                      headers=self.headers,
                      dont_filter=True
                      )

    def parse_page(self, response):

        page_links = []
        page_link = response.xpath('//span[@class="pagnLink"]/a/@href')[0].extract()
        page_link_num = response.xpath('//span[@class="pagnLink"]/a/text()')[0].extract()
        page_count = response.xpath('//span[@class="pagnDisabled"]/text()')[0].extract()

        for page_num in range(1, int(page_count)):
            page_list = page_link.replace('page={page_link_num}'.format(page_link_num=int(page_link_num)),
                                          'page={page_num}'.format(page_num=page_num))
            page_list = self.START_URL + page_list
            page_links.append(page_list)

        for p_link in page_links:
            if 'https' in p_link:
                sub_link = p_link
            else:
                sub_link = self.START_URL + p_link
            yield Request(url=sub_link, callback=self.parse_data, dont_filter=True, headers=self.headers)

    def parse_data(self, response):
        li_list = response.xpath("//div[@id='mainResults']/.//ul/li [contains(@id, 'result')]")
        for li in li_list:
            link = li.xpath(".//div[contains(@class, 'a-spacing-mini')]//a[contains(@class,'s-access-detail-page')]/@href").extract()
            try:
                if link and 'http' in link[0]:
                    yield Request(url=link[0],
                                  callback=self.parse_product,
                                  dont_filter=True,
                                  headers=self.headers)

            except Exception as e:
                print (link[0])

    def parse_product(self, response):
        product = SiteProductItem()

        title = self._parse_title(response)
        product['title'] = title

        brand = self._parse_brand(response)
        product['brand'] = brand

        price = self._parse_price(response)
        product['price'] = price

        original_price = self._parse_original_price(response)
        product['original_price'] = original_price

        yield product

    @staticmethod
    def _parse_title(response):
        title = response.xpath("//span[@id='productTitle']/text()").extract()
        return title[0].strip() if title else None

    @staticmethod
    def _parse_brand(response):
        brand_info = response.xpath('//a[@id="brand"]/@href').extract()
        if not brand_info:
            brand_info = response.xpath('//a[@id="brand"]/text()').extract()
        if not brand_info:
            brand_info = response.xpath('//*[@id="by-line"]/.//a/text()').extract()
        brand = None
        if brand_info:
            brand = brand_info[0].split('/')[1].split('/')[0]
        return brand

    @staticmethod
    def _parse_price(response):
        price = response.xpath('//span[contains(@id,"priceblock")]/text()').extract()
        return price[0].split('-')[0] if price else None

    @staticmethod
    def _parse_original_price(response):
        original_price = response.xpath('//span[contains(@class,"a-text-strike")]/text()').extract()
        if not original_price:
            original_price = response.xpath('//span[contains(@id,"priceblock")]/text()').extract()
        return original_price[0].split('-')[0] if original_price else None


