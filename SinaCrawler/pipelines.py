# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html
from scrapy import signals
from scrapy.exceptions import DropItem
from scrapy.exporters import CsvItemExporter

from SinaCrawler.items import Gu8Item, Gu8User, Gu8Comment
from SinaCrawler.spiders.gu8_spider import Gu8Spider
from SinaCrawler.spiders.sina_spider import WeiboSpider
from utils.DatabaseConnection import DatabaseConnection
import sys

# set the default encoding to utf-8
# reload sys model to enable the getdefaultencoding method.
reload(sys)
# using exec to set the encoding, to avoid error in IDE.
exec "sys.setdefaultencoding('utf-8')"


class SinacrawlerPipeline(object):

    item_record = {}

    def process_weibo(self, item):
        if item['mid'] in self.item_record[type(item).__name__]:
            raise DropItem()
        self.item_record[type(item).__name__].add(item['mid'])
        conn = DatabaseConnection().get_connection()
        cursor = conn.cursor()
        sql_check = u"select count(*) as num from weibo_data where weibo_id = '%s'" % item["mid"]
        cursor.execute(sql_check)
        result = cursor.fetchall()
        print result
        if result[0][u'num'] != 0:
            raise DropItem("Crawled item")
        else:
            user_check = u"select count(*) as num from weibo_account where user_id = '%s'" % item["user_id"]
            cursor.execute(user_check)
            result = cursor.fetchall()
            if result[0][u'num'] == 0:
                user_insert = u"insert into weibo_account(user_id, user_name) values('%s', '%s')" %\
                              (item["user_id"], item["user_name"].encode('utf-8'))
                print user_insert
                cursor.execute(user_insert)
            if item["father_mid"] is None:
                item["father_mid"] = ""
            sql_base = u"insert into weibo_data(weibo_id, user_id, father_id, pubtime, key_word, like_num, content)" \
                       " values(\"%s\", \"%s\", \"%s\", \"%s\", \"%s\", \"%s\", \"%s\")" % \
                       (item['mid'], item['user_id'],
                        item['father_mid'], item['time'],
                        item['keyword'].encode('utf-8'), item['like'],
                        item['content'].encode('utf-8'))

            cursor.execute(sql_base)
            cursor.close()
            return item

    def process_gu8(self, item, spider):
        if isinstance(item, Gu8Item):
            if (item['id'], item['stock']) in self.item_record[type(item).__name__]:
                raise DropItem()
            self.item_record[type(item).__name__].add((item['id'], item['stock']))
            conn = DatabaseConnection().get_connection()
            cursor = conn.cursor()
            sql_check = u"select count(*) as num from gu8_item where id = '%s' and stock = '%s'" % (item["id"], item['stock'])
            cursor.execute(sql_check)
            result = cursor.fetchall()
            print result
            if result[0][u'num'] != 0:
                spider.call_back(item, False)
                raise DropItem("Crawled item")
            sql_base = u"insert into gu8_item(stock, id, favor, title, time, forward, content, user_id)" \
                       " values(\"%s\", \"%s\", \"%s\", \"%s\", \"%s\", \"%s\", \"%s\", \"%s\")" % \
                       (item['stock'], item['id'],
                        item['like'], item['title'].encode('utf-8'),
                        item['time'], item['forward'],
                        item['content'].encode('utf-8'), item['user_id'])
            cursor.execute(sql_base)
            cursor.close()
        elif isinstance(item, Gu8User):
            if item['user_id'] in self.item_record[type(item).__name__]:
                raise DropItem()
            self.item_record[type(item).__name__].add(item['user_id'])
            conn = DatabaseConnection().get_connection()
            cursor = conn.cursor()
            sql_check = u"select count(*) as num from gu8_user where user_id = '%s'" % (item["user_id"])
            cursor.execute(sql_check)
            result = cursor.fetchall()
            print result
            if result[0][u'num'] != 0:
                raise DropItem("Crawled item")
            sql_base = u"insert into gu8_user(user_id, age, influence, user_name, influence_range)" \
                       " values(\"%s\", \"%s\", \"%s\", \"%s\", \"%s\")" % \
                       (item['user_id'], item['age'],
                        item['influence'], item['user_name'].encode('utf-8'),
                        item['influence_range'].encode('utf-8'))
            cursor.execute(sql_base)
            cursor.close()
        elif isinstance(item, Gu8Comment):
            if (item['id'], item['user_id']) in self.item_record[type(item).__name__]:
                raise DropItem()
            self.item_record[type(item).__name__].add((item['id'], item['user_id']))
        return item

    def process_item(self, item, spider):
        if type(item).__name__ not in self.item_record:
            self.item_record[type(item).__name__] = set()
        if isinstance(spider, WeiboSpider):
            return self.process_weibo(item)
        elif isinstance(spider, Gu8Spider):
            return self.process_gu8(item, spider)


class StoragePipeline(object):

    file_format = "output/{0}_output.csv"

    exporters = {}

    files = {}

    @classmethod
    def from_crawler(cls, crawler):
        pipeline = cls()
        crawler.signals.connect(pipeline.spider_opened, signals.spider_opened)
        crawler.signals.connect(pipeline.spider_closed, signals.spider_closed)
        return pipeline

    def spider_opened(self, spider):
        self.files[spider.name] = {}
        self.exporters[spider.name] = {}

    def process_item(self, item, spider):
        if type(item).__name__ not in self.files[spider.name]:
            self.files[spider.name][type(item).__name__] = open(self.file_format.format(type(item).__name__), 'w+b')
            self.exporters[spider.name][type(item).__name__] = \
                CsvItemExporter(self.files[spider.name][type(item).__name__])
        self.exporters[spider.name][type(item).__name__].export_item(item)
        return item

    def spider_closed(self, spider):
        exporters = self.exporters.pop(spider.name)
        files = self.files.pop(spider.name)
        for name in exporters:
            exporter = exporters[name]
            exporter.finish_exporting()
        for name in files:
            file_ = files[name]
            file_.close()
