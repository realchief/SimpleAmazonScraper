# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://doc.scrapy.org/en/latest/topics/item-pipeline.html
import re


class AmazonscraperPipeline(object):
    def process_item(self, item, spider):
        origin_price = re.search('\d+\.?\d*', item['original_price']).group()
        price = re.search('\d+\.?\d*', item['price']).group()
        discount_rate = str(((float(origin_price)-float(price))/float(price))*100) + "%"

        item['discount_rate'] = discount_rate
        return item
