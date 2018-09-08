# -*- coding: utf-8 -*-
import scrapy
from scrapy.exceptions import IgnoreRequest

from SinaCrawler.spiders.gu8_spider import Gu8Spider


class Gu8MiddleWare(object):

    _url_dict = {}

    _user_dict = []

    def process_request(self, request, spider):
        if not isinstance(spider, Gu8Spider):
            return None
        if 'stock_code' in request.meta:
            if request.meta['stock_code'] not in self._url_dict:
                self._url_dict[request.meta['stock_code']] = []
            if request.url in self._url_dict[request.meta['stock_code']]:
                return IgnoreRequest
            else:
                self._url_dict[request.meta['stock_code']].add(request.url)
                return None
        elif '_user_id' in request.meta:
            if request.meta['_user_id'] in self._user_dict:
                return IgnoreRequest
        return None

    def process_response(self, request, response, spider):
        if not isinstance(spider, Gu8Spider):
            return response
        if '_user_id' in response.meta and 'already' not in response.meta:
            self._user_dict.append(response.meta['_user_id'])
            return response



