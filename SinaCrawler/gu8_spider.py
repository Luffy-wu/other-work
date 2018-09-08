# -*- coding: utf-8 -*-
import json

import scrapy

from SinaCrawler.items import Gu8User, Gu8Item, Gu8Comment
import datetime


class Gu8Spider(scrapy.Spider):
    headers = {
        'Accept': 'image/webp,image/*,*/*;q=0.8',
        'Accept-Encoding': 'gzip, deflate, sdch',
        "Accept-Language": "zh-CN,zh;q=0.8",
        "Connection": "keep-alive",
        "Content-Type": " application/x-www-form-urlencoded; charset=UTF-8",
        'Host': 'guba.eastmoney.com',
        'Referer': 'http://guba.eastmoney.com/list,{0}_1.html'
    }

    referer_format = 'http://guba.eastmoney.com/list,{0}_1.html'

    _users = {}

    _articles = {}

    allowed_domains = ['guba.eastmoney.com', 'passport.eastmoney.com', 'iguba.eastmoney.com']

    name = 'gu8_spider'

    _basiinfo = 'https://passport.eastmoney.com/pub/basicinfo'

    _cookie_key = 'gu8_cookies'

    _stocks = []

    _stock_index = 0 
    
    _user = ()

    _url_root = 'http://guba.eastmoney.com'

    _url_format = "http://guba.eastmoney.com/list,{0},f_{1}.html"

    _current_page = 1

    _old_count = 0

    _user_root = "http://iguba.eastmoney.com/interf/user.aspx?action=floatinfo&uid="

    _max_page = 1

    _first = True

    _start_time = 0

    _end_time = 0

    _cur_month = datetime.datetime.now().month

    _cur_year = datetime.datetime.now().year

    @property
    def current_url(self):
        return self._url_format.format(self._stocks[self._stock_index], self._current_page)

    @current_url.getter
    def current_url(self):
        result = self._url_format.format(self._stocks[self._stock_index], self._current_page)
        self._current_page += 1
        return result if self._current_page < self._max_page + 2 else 0

    def call_back(self, item, result):
        if not result:
            self._old_count += 1

    def next_stock(self):
        if self._stock_index < len(self._stocks):
            self._stock_index += 1
            self._current_page = 1
            self._max_page = 1
            self._cur_month = datetime.datetime.now().month
            self._cur_year = datetime.datetime.now().year
            self._old_count = 1
            self._articles = {}
            self.headers['Referer'] = self.referer_format.format(self._stocks[self._stock_index])
            self._first = True
            return True
        else:
            return False

    def __init__(self, stocks, start_time, end_time, *args, **kwargs):
        super(Gu8Spider, self).__init__(*args, **kwargs)
        self._stocks = stocks
        self.headers['Referer'] = self.referer_format.format(stocks[0])
        self._user = ['13469981619', 'qiao1rui']
        self._start_time = datetime.datetime.strptime(start_time, '%Y-%m-%d')
        self._end_time = datetime.datetime.strptime(end_time, '%Y-%m-%d')

    def start_requests(self):
        return [scrapy.Request('https://passport.eastmoney.com/pub/login', meta={'cookiejar': self._cookie_key},
                               headers=self.headers, callback=self.before_login)]

    def before_login(self, response):
        return scrapy.FormRequest(url='https://passport.eastmoney.com/pub/JsonAPI/Login',
                                  formdata={'username': self._user[0], 'password': self._user[1]},
                                  meta={'cookiejar': response.meta['cookiejar']}, callback=self.after_login)

    def after_login(self, response):
        print response
        result = json.loads(response.body.encode('unicode-escape'))
        print result
        if 'rc' in result and result['rc'] == True:
            yield scrapy.Request(url=self._basiinfo, meta={'cookiejar': response.meta['cookiejar']},
                                 callback=self.before_parse, headers=self.headers)

    def before_parse(self, response):
        yield scrapy.Request(url=self.current_url, meta={'cookiejar': response.meta['cookiejar']},
                             callback=self.parse, headers=self.headers)

    def parse(self, response):
        root = response.selector
        first_flag = True
        if self._first:
            max_page = root.xpath("//span[@class='pagernums']/@data-pager").extract_first()
            if max_page is None or max_page == '':
                first_flag = False
                if self.next_stock():
                    yield scrapy.Request(url=self.current_url, meta={'cookiejar': response.meta['cookiejar']},
                                    callback=self.parse, headers=self.headers)
                else:
                    yield None
            else:
                page_list = max_page.split('|')
                print page_list
                self._max_page = int(page_list[-3]) / int(page_list[-2]) + 1
                print self._max_page
        if first_flag and self._old_count > 5:
            if self.next_stock():
                yield scrapy.Request(url=self.current_url, meta={'cookiejar': response.meta['cookiejar']},
                                 callback=self.parse, headers=self.headers)
            else:
                yield None
        elif first_flag:
            divs = root.xpath("//div[@class='articleh odd' or @class='articleh']")
            flag = 0
            count = 0
            count_l = 0
            pre_month = self._cur_month
            for div in divs:
                a = div.xpath('.//span[@class="l3"]/a')
                results = div.xpath('.//span[@class="l6"]/text()').extract_first()
                month = int(results[0:2])
                day = int(results[3:])
                print self._cur_month
                if month < pre_month and month > pre_month - 2:
                    self._cur_month = month
                    pre_month = month
                elif month < pre_month - 2:
                    count_l += 1
                    if count_l > 7:
                        self._cur_month = month
                        pre_month = month
                elif month > pre_month + 4:
                    count += 1
                    if count > 3:
                        self._cur_month = month
                        pre_month = month
                        self._cur_year -= 1
                time_now = datetime.datetime(year=self._cur_year, month=month, day=day)
                print time_now
                if type(a) == list:
                    a = a[0]
                url = a.xpath('@href').extract_first()
                stock = url.split(',')[1]
                url = self._url_root + url if url[0] == '/' else self._url_root + '/' + url
                if time_now >= self._start_time and time_now <= self._end_time:
                    print '222222222222222222222222222222222'
                    yield scrapy.Request(url=url, headers=self.headers, callback=self.parse_inner,
                                    meta={'cookiejar': response.meta['cookiejar'], 'stock_code': stock})
                elif self._start_time > time_now:
                    flag += 1
            url = self.current_url
            if self._first:
                self._first = False
            if url != 0 and flag < 5:
                yield scrapy.Request(url=url, meta={'cookiejar': response.meta['cookiejar']},
                                    callback=self.parse, headers=self.headers)
            else:
                if self.next_stock():
                    yield scrapy.Request(url=self.current_url, meta={'cookiejar': response.meta['cookiejar']},
                                    callback=self.parse, headers=self.headers)
                else:
                    yield None

    def parse_inner(self, response):
        url = response.url
        article_id = url.split(',')[-1].split('.')[0]
        stock = url.split(',')[-2]
        pos = article_id.find('_')
        page = 1
        if pos != -1:
            article_id = article_id[0:pos]
            page = article_id[pos + 1:]
        root = response.selector
        print stock + ' ' + article_id + ' ' + str(page)
        if 'stock_code' in response.request.meta:
            main_item = root.xpath("//div[@id='zwcontent']")
            user_id = None
            if len(main_item.xpath(".//div[@id='zwconttbn']/span[@data-uid>0]")) > 0:
                user_id = main_item.xpath(".//div[@id='zwconttbn']/span[@class='influence']/@data-uid").extract_first()
                print user_id
                yield scrapy.Request(url=self._user_root + user_id,
                                     meta={'cookiejar': response.meta['cookiejar'], '_user_id': user_id},
                                     callback=self.parse_user, headers=self.headers)
            main_content = Gu8Item()
            main_content['id'] = article_id
            main_content['user_id'] = user_id
            time = main_item.xpath(".//div[@class='zwfbtime']/text()"). \
                re_first('^.+?(\d{4}-\d{2}-\d{2}\s*\d{2}:\d{2}:\d{2}).+$')
            print time
            main_content['time'] = time
            main_content['title'] = main_item.xpath(".//div[@id='zwconttbt']/text()").extract_first().encode('utf-8')
            main_content['stock'] = response.request.meta['stock_code']
            text = u""
            for txt in main_item.xpath(".//div[@id='zwconbody']//text()").extract():
                text += txt.encode('utf-8')
            main_content['content'] = text
            forward = main_item.xpath(".//span[@id='zfnums']/text()").extract()
            if len(forward) >= 1:
                main_content['forward'] = forward[0]
            else:
                main_content['forward'] = 0
            self._articles[article_id] = main_content
            yield scrapy.Request(
                url='http://iguba.eastmoney.com/interf/guba.aspx?action=getpraise&id=' + article_id,
                headers=self.headers,
                meta={'article_id': article_id, 'cookiejar': response.meta['cookiejar']},
                callback=self.parse_article_like)
        # comments = root.xpath('//div[@id="zwlist"]/div[@class="zwli clearfix"]')
        # group = {}
        # if article_id not in self._comments:
        #     self._comments[article_id] = {}
        # for item in comments:
        #     content = item.xpath('.//div[@class="zwlitxt"]')
        #     gu8_comment = Gu8Comment()
        #     user_part = content.xpath('.//span[@class="influence"]/@data-uid').extract_first()
        #     gu8_comment['user_id'] = user_part
        #     time = item.xpath(".//div[@class='zwlitime']/text()").re_first(
        #         '^.+?(\d{4}-\d{2}-\d{2}\s*\d{2}:\d{2}:\d{2}).*$')
        #     # print time
        #     gu8_comment['time'] = time
        #     text = u''
        #     text_part = item.xpath('.//div[@class="zwlitext stockcodec"]//text()')
        #     for txt in text_part.extract():
        #         text += txt
        #     gu8_comment['content'] = text
        #     cid = item.xpath('@data-huifuid').extract_first()
        #     gu8_comment['id'] = cid
        #     gu8_comment['article'] = article_id
        #     self._comments[article_id][cid] = gu8_comment
        #     group[cid] = user_part
        # param = u''
        # for item in group:
        #     param += item + '%7C' + group[item] + '%2C'
        # param = param[:-1]
        # yield scrapy.Request(
        #     url='http://iguba.eastmoney.com/interf/guba.aspx?action=getreplylikegd&id=' + article_id + '&replyids=' +
        #         param + "&code=" + stock, headers=self.headers,
        #     meta={'article_id': article_id, 'cookiejar': response.meta['cookiejar']},
        #     callback=self.parse_like)

    def parse_article_like(self, response):
        if 'article_id' in response.meta:
            item = self._articles.pop(response.meta['article_id'])
            like = json.loads(response.body[1:-1])['count']
            item['like'] = like
            yield item

    def parse_like(self, response):
        if 'article_id' in response.meta:
            comments = json.loads(response.body[1:-1])['result']
            items = self._comments.pop(response.meta['article_id'])
            print comments
            print items
            print "213333333333333333333333"
            for comment in comments:
                items[str(comment['id'])]['like'] = comment['count']
            for item in items:
                yield item

    def parse_user(self, response):
        if 'already' not in response.meta:
            item = json.loads(response.body[1:-1])
            user = Gu8User()
            user['user_name'] = item['user_nickname']
            user['user_id'] = item['user_id']
            user['influence'] = item['user_influ_level']
            user['age'] = item['user_age'][0:-1]
            stocks = item['user_influ_range']
            stock_inf = u''
            for i in stocks:
                stock_inf += i['stockbar_name'] + u' ' + i['stockbar_market'] + '-'
            user['influence_range'] = stock_inf[0:-1]
            yield user
