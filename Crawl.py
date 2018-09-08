# coding= UTF-8
from scrapy.crawler import CrawlerProcess
from scrapy.utils.project import get_project_settings
import tushare as ts

stock_list = ts.get_stock_basics().reset_index()['code'].tolist()

def main():
    settings = get_project_settings()
    
   
    process = CrawlerProcess(settings)
    # process.crawl("weibo_spider", keyword=v, crawl_start_time="2015-01-01", crawl_end_time="2015-07-01")
    process.crawl("gu8_spider", stocks=stock_list, start_time='2016-08-31', end_time='2016-09-15')
    process.start()

print "Spider start"
main()
