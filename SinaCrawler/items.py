# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html

import scrapy


class WeiboItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    user_name = scrapy.Field()
    user_id = scrapy.Field()
    content = scrapy.Field()
    time = scrapy.Field()
    like = scrapy.Field()
    mid = scrapy.Field()
    keyword = scrapy.Field()
    father_mid = scrapy.Field()

    def __eq__(self, other):
        if isinstance(other, WeiboItem):
            if other['mid'] == self['mid']:
                return True
        return False


class Gu8Item(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    title = scrapy.Field()
    user_id = scrapy.Field()  # fk， nullable
    content = scrapy.Field()
    time = scrapy.Field()
    like = scrapy.Field()
    stock = scrapy.Field()  # cpk
    forward = scrapy.Field()
    id = scrapy.Field()  # cpk

    def __eq__(self, other):
        if isinstance(other, Gu8Item):
            if other['id'] == self['id'] and self['stock'] == other['stock']:
                return True
        return False


class Gu8User(scrapy.Item):
    user_id = scrapy.Field()  # pk
    user_name = scrapy.Field()
    influence = scrapy.Field()
    influence_range = scrapy.Field()
    age = scrapy.Field()

    def __eq__(self, other):
        if isinstance(other, Gu8User):
            if other['user_id'] == self['user_id']:
                return True
        return False


class Gu8Comment(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    user_id = scrapy.Field()  # fk， nullable
    content = scrapy.Field()
    time = scrapy.Field()
    like = scrapy.Field()
    article = scrapy.Field()  # fk
    id = scrapy.Field()  # pk

    def __eq__(self, other):
        if isinstance(other, Gu8Comment):
            if other['id'] == self['id'] and self['user_id'] == other['user_id']:
                return True
        return False
