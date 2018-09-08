# -*- coding: utf-8 -*-
import base64
import hashlib
import json
import re
import urllib

import binascii
import rsa
from scrapy.http.cookies import CookieJar
from scrapy.spiders import Spider
import scrapy
import time
from SinaCrawler.items import WeiboItem
from scrapy.selector import Selector
import datetime
import random
import sys

reload(sys)
sys.setdefaultencoding("utf-8")


class WeiboSpider(Spider):

    ATTRS={
        "CURRENT_ITEM_INDEX": 0
    }

    SINA_USERS = {
        "qiao8miku@sina.cn": "qiao1rui",
        "hqdandan1@163.com": "Q1w2e3r4"
    }

    def get_user(self):
        if self.ATTRS["CURRENT_ITEM_INDEX"] < len(self.SINA_USERS):
            result = [self.SINA_USERS.keys()[self.ATTRS["CURRENT_ITEM_INDEX"]],
             self.SINA_USERS.get(self.SINA_USERS.keys()[self.ATTRS["CURRENT_ITEM_INDEX"]])]
            self.ATTRS["CURRENT_ITEM_INDEX"] = divmod(self.ATTRS["CURRENT_ITEM_INDEX"] + 1, len(self.SINA_USERS))[1]
            return result

    _from_time_scope = ""

    _origin_from_time_scope = ""

    _to_time_scope = ""

    _cookie_key = 'sina_cookies'

    name = "weibo_spider"

    allowed_domains = ["weibo.com", "sina.com.cn"]

    _url_root = "http://s.weibo.com/weibo/"

    _default_param = None

    _error = False

    _current_page = 0

    _max_page = 34

    _keyword_origin = []

    _current_time = None

    download_delay = 10.0

    _first = True

    _user = ()

    _format = "%Y-%m-%d-%H"

    _format_old = "%Y-%m-%d"

    _key = ""

    _change = False

    _current_keyword = 0

    _finish = False

    def call_back(self, item, result):
        pass

    def get_pwd_wsse(self, pwd, servertime, nonce):
        """
            Get wsse encrypted password
        """
        pwd1 = hashlib.sha1(pwd).hexdigest()
        pwd2 = hashlib.sha1(pwd1).hexdigest()
        pwd3_ = pwd2 + servertime + nonce
        pwd3 = hashlib.sha1(pwd3_).hexdigest()
        return pwd3

    def get_pwd_rsa(self, pwd, servertime, nonce):
        """
            Get rsa2 encrypted password, using RSA module from https://pypi.python.org/pypi/rsa/3.1.1, documents can be accessed at
            http://stuvel.eu/files/python-rsa-doc/index.html
        """
        # n, n parameter of RSA public key, which is published by WEIBO.COM
        # hardcoded here but you can also find it from values return from prelogin status above
        weibo_rsa_n = 'EB2A38568661887FA180BDDB5CABD5F21C7BFD59C090CB2D245A87AC253062882729293E5506350508E7F9AA3BB77F4333231490F915F6D63C55FE2F08A49B353F444AD3993CACC02DB784ABBB8E42A9B1BBFFFB38BE18D78E87A0E41B9B8F73A928EE0CCEE1F6739884B9777E4FE9E88A1BBE495927AC4A799B3181D6442443'

        # e, exponent parameter of RSA public key, WEIBO uses 0x10001, which is 65537 in Decimal
        weibo_rsa_e = 65537
        message = str(servertime) + '\t' + str(nonce) + '\n' + str(pwd)

        # construct WEIBO RSA Publickey using n and e above, note that n is a hex string
        key = rsa.PublicKey(int(weibo_rsa_n, 16), weibo_rsa_e)

        # get encrypted password
        encropy_pwd = rsa.encrypt(message, key)
        # trun back encrypted password binaries to hex string
        return binascii.b2a_hex(encropy_pwd)

    def get_user(self, username):
        username_ = urllib.quote(username)
        username = base64.encodestring(username_)[:-1]
        return username

    @property
    def time_scope(self):
        return ""

    @time_scope.setter
    def time_scope(self, values):
        if values[0] != 0:
            if values[0].count('-') == 3:
                self._origin_from_time_scope = datetime.datetime.strptime(values[0], self._format)
            else:
                self._origin_from_time_scope = datetime.datetime.strptime(values[0], self._format_old)
            self._from_time_scope = self._origin_from_time_scope
        else:
            self._from_time_scope = None
        if values[1] != 0:
            if values[1].count('-') == 3:
                self._to_time_scope = datetime.datetime.strptime(values[1], self._format)
            else:
                self._to_time_scope = datetime.datetime.strptime(values[1], self._format_old)
        else:
            self._to_time_scope = None

    @time_scope.getter
    def time_scope(self):
        if self._from_time_scope is None or self._to_time_scope is None:
            return ""
        if self._change:
            self._from_time_scope = self._origin_from_time_scope
        return "&timescope=custom:" + self._from_time_scope.strftime(self._format) + \
               ":" + self._to_time_scope.strftime(self._format)

    def __init__(self, keywords, crawl_start_time=0, crawl_end_time=0, *args, **kwargs):
        super(WeiboSpider, self).__init__(*args, **kwargs)
        self.time_scope = [crawl_start_time, crawl_end_time]
        self._current_time = crawl_end_time
        self.keyword = keywords
        self._user = self.get_user()
        

    @property
    def keyword(self):
        return self._key

    @keyword.setter
    def keyword(self, value):
        self._keyword_origin = value
        self._key = urllib.quote(value[0].encode('utf-8'))

    @keyword.getter
    def keyword(self):
        if self._change:
            self._current_keyword += 1
            if self._current_keyword >= len(self._keyword_origin):
                self._finish = True
                return ""
            self._key = urllib.quote(self._keyword_origin[self._current_keyword].encode('utf-8'))
        return self._key.replace("%", "%25")

    @property
    def current_page(self):
        return self._current_page

    @current_page.getter
    def current_page(self):
        if self._change:
            self._current_page = 1
        elif self._current_page == 50:
            self._current_page = 1
        elif self._error:
            self._error = False
        else:
            self._current_page += 1
        return "&page=" + str(self._current_page)

    def get_url(self):
        url = self._url_root + self.keyword + self.time_scope + "&nodup=1" + self.current_page
        if self._change:
            self._change = False
        return url

    def start_requests(self):
        request = scrapy.Request(
            'http://login.sina.com.cn/sso/prelogin.php?entry=weibo&callback=sinaSSOController.preloginCallBack&su=' +
            self.get_user(self._user[0]) + '&rsakt=mod&checkpin=1&client=ssologin.js(v1.4.11)',
            callback=self.parse_prelogin, method='GET', meta={'cookiejar': self._cookie_key}, dont_filter=True)
        
        return [request, ]

    def timestamp_datetime(self, value):
        value_format = '%Y-%m-%d %H:%M:%S'
        # value为传入的值为时间戳(整形)，如：1332888820
        value = time.localtime(value)
        # 经过localtime转换后变成
        # time.struct_time(tm_year=2012, tm_mon=3, tm_mday=28, tm_hour=6, tm_min=53,
        # tm_sec=40, tm_wday=2, tm_yday=88, tm_isdst=0)
        # 最后再经过strftime函数转换为正常日期格式。
        dt = time.strftime(value_format, value)
        return dt

    def after_logout(self, response):

        self._user = self.get_user()
        yield self.start_requests()[0]

    def parse(self, response):
        # print response.body
        results = response.selector.xpath("//script/text()").re('.+?"pid":"pl_weibo_direct".+?"html":"(.+)"}\)')
        latest_time = None
        if len(results) == 0:
            self._error = True
            request = scrapy.Request("http://weibo.com/logout.php", meta={'cookiejar': response.meta['cookiejar']},
                                     callback=self.after_logout, dont_filter=True)
            yield request
        else:
            out = results[0].replace('\\"', '"').replace("\\n", "").replace("\\/", "/").replace("\\\\", "\\"). \
                decode("unicode-escape")
            root = Selector(text=out)
            if self._first:
                self._first = False
                page_max = root.xpath("//div[@class='W_pages']//li/a/text()")[-1].re(u"^.*第(\d+)页.*$")
                print page_max
                self._max_page = int(page_max[0])
            divs = root.xpath("//div[@action-type='feed_list_item']")
            for div in divs:
                print div
                item = WeiboItem()
                item["keyword"] = self._keyword_origin
                item["father_mid"] = ""
                item["mid"] = div.xpath("@mid").extract()
                if type(item['mid']) == list:
                    item['mid'] = item['mid'][0]
                item["user_name"] = unicode(div.xpath(".//img[@class='W_face_radius']/@alt").extract_first())

                user_id = div.xpath(".//img[@class='W_face_radius']/@usercard").extract_first()
                print user_id
                pattern = re.compile(r"^.*id=(\d+)&.+$")
                match = pattern.match(user_id)
                item["user_id"] = match.group(1)
                text = u""
                texts = div.xpath(".//p[@class='comment_txt']/text()").extract()
                for txt in texts:
                    text += txt
                item["content"] = text
                item["like"] = div.xpath(
                    ".//div[@class='feed_action clearfix']/ul/li[last()]//em/text()").extract_first()
                if item["like"] is None:
                    item["like"] = 0
                timestamp = int(div.xpath(".//div[@class='content clearfix']/div/a[@class='W_textb']/"
                                          "@date").extract_first()) / 1000
                item["time"] = self.timestamp_datetime(timestamp)
                print item
                if self._current_page == 50:
                    latest_time = item["time"]
                fathers = div.xpath(".//div[@class='comment']")
                if len(fathers) != 0:
                    father = fathers[0]
                    father_user_id = father.xpath(
                        ".//div[@node-type='feed_list_forwardContent']/a/@usercard").extract_first()
                    print father_user_id
                    if father_user_id is not None:
                        father_item = WeiboItem()
                        father_item["keyword"] = self._keyword_origin
                        father_mid = father.xpath(".//ul[@class='feed_action_info']//a")[-1].xpath(
                            "@action-data").re_first("^mid=(\d+)$")
                        item["father_mid"] = father_mid
                        father_item["mid"] = father_mid
                        father_item["user_name"] = unicode(father.xpath(
                            ".//div[@node-type='feed_list_forwardContent']/a/@nick-name").extract_first())
                        match = pattern.match(father_user_id)
                        father_item["user_id"] = match.group(1)
                        texts = father.xpath(".//p[@class='comment_txt']/text()").extract()
                        text = u""
                        father_item["father_mid"] = ""
                        for txt in texts:
                            text += txt
                        father_item["content"] = text
                        timestamp = int(
                            father.xpath(".//div[@class='feed_from W_textb']/a/@date").extract_first()) / 1000
                        father_item["time"] = self.timestamp_datetime(timestamp)
                        father_item["like"] = father.xpath(".//ul[@class='feed_action_info']//em")[-1].xpath(
                            "text()").extract_first()
                        if father_item["like"] is None:
                            father_item["like"] = 0
                        yield father_item
                yield item
            time.sleep(random.randint(0, 5))
            if self._current_page < self._max_page:
                request = scrapy.Request(self.get_url(), meta={'cookiejar': response.meta['cookiejar']},
                                         callback=self.parse, dont_filter=True)
                yield request
            elif self._max_page == 50:
                self._to_time_scope = datetime.datetime.strptime(latest_time, "%Y-%m-%d %H:%M:%S")
                if self._to_time_scope >= self._from_time_scope:
                    self._first = True
                    request = scrapy.Request(self.get_url(), meta={'cookiejar': response.meta['cookiejar']},
                                             callback=self.parse, dont_filter=True)
                    
                    yield request
            else:
                self._change = True
                request = scrapy.Request(self.get_url(), meta={'cookiejar': response.meta['cookiejar']},
                                                callback=self.parse, dont_filter=True)
                if self._finish:
                    yield None
                else:
                    yield request
            


    def parse_prelogin(self, response):
        """
        Perform prelogin action, get prelogin status, including servertime, nonce, rsakv, etc.
        :param response:
        """
        # prelogin_url = 'http://login.sina.com.cn/sso/prelogin.php?entry=weibo&callback=sinaSSOController.preloginCallBack&client=ssologin.js(v1.4.5)'

        p = re.compile('\((.*)\)')

        try:
            json_data = p.search(response.body).group(1)
            data = json.loads(json_data)
            servertime = str(data['servertime'])
            nonce = data['nonce']
            rsakv = data['rsakv']
            login_data = {'entry': 'weibo', 'gateway': '1', 'from': '', 'savestate': '7', 'userticket': '1',
                          'pagerefer': '', 'vsnf': '1', 'su': self.get_user(self._user[0]), 'service': 'miniblog',
                          'servertime': servertime, 'nonce': nonce, 'pwencode': 'rsa2', 'rsakv': rsakv,
                          'sp': self.get_pwd_rsa(self._user[1], servertime, nonce), 'encoding': 'UTF-8', 'prelt': '45',
                          'url': 'http://weibo.com/ajaxlogin.php?framelogin=1&callback=parent.sinaSSOController.feedBackUrlCallBack',
                          'returntype': 'META'}
            login_url = 'http://login.sina.com.cn/sso/login.php?client=ssologin.js(v1.4.11)'
            return scrapy.FormRequest(url=login_url, formdata=login_data,
                                      meta={'cookiejar': response.meta['cookiejar']},
                                      callback=self.parse_afterlogin, dont_filter=True)
        except:
            print 'Getting prelogin status met error!'
            return None

    def parse_afterlogin(self, response):
        """
        Perform after login action, get prelogin status, including servertime, nonce, rsakv, etc.
        :param response:
        """
        # prelogin_url = 'http://login.sina.com.cn/sso/prelogin.php?entry=weibo&callback=sinaSSOController.preloginCallBack&client=ssologin.js(v1.4.5)'
        print response.url
        p = re.compile('location\.replace\([\"\'](.*?)[\"\']\)')
        patt_feedback = 'feedBackUrlCallBack\((.*)\)'
        p2 = re.compile(patt_feedback, re.MULTILINE)
        print response.request.cookies
        try:
            if 'inner' in response.meta:
                print '66666666666666666666'
                feedback = p2.search(response.body).group(1)
                feedback_json = json.loads(feedback)
                print feedback_json
                if feedback_json['result']:
                    return scrapy.Request(url=self.get_url(), meta={'cookiejar': response.meta['cookiejar']},
                                          callback=self.parse, dont_filter=True)
                else:
                    return 1
            else:
                login_url = p.search(response.body).group(1)
                print '23333333333333333333'
                print login_url
                return scrapy.Request(url=login_url, meta={'cookiejar': response.meta['cookiejar'], 'inner': True},
                                      callback=self.parse_afterlogin, dont_filter=True)
        except:
            print 'Getting afterlogin status met error!'
            return None
