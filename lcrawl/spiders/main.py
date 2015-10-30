# -*- coding: utf-8 -*-

import urlparse

import scrapy
from scrapy.exceptions import CloseSpider
from scrapy.http import Request

from lcrawl.loading import load_callable_chain, \
    load_obj_and_call, DictUnion, FirstCaller 


class MainSpider(scrapy.Spider):
    name = "main"

    def __init__(self, seeds_file,
                 decision_function,
                 transition_extractors,
                 page_analyzers):
        self.seeds_file = seeds_file
        self.decision_function = decision_function
        self.transition_extractors = transition_extractors
        self.page_analyzers = page_analyzers

    @classmethod
    def from_crawler(cls, crawler):
        return cls(crawler.settings.get('SEEDS_FILE'),
                   load_obj_and_call(crawler.settings.get('DECISION_FUNCTION')),
                   load_callable_chain(crawler.settings.get('TRANSITION_EXTRACTORS'),
                                       DictUnion),
                   load_callable_chain(crawler.settings.get('PAGE_ANALYZERS'),
                                       FirstCaller))

    def start_requests(self):
        with open(self.seeds_file, 'r') as f:
            for line in f:
                line = line.strip()
                parsed = urlparse.urlparse(line)
                if not parsed.hostname():
                    parsed = urlparse.urlparse('http://' + line)
                url = parsed.geturl()
                yield Request(url,
                              meta = {
                                      'state' : self.decision_function.get_initial_state(url)
                                      })

    def parse(self, response):
        if response.status >= 400:
            return
        decision = self.decision_function.decide(response.meta['state'],
                                                 self.page_analyzers(response),
                                                 self.transition_extractors(response))
        for item in decision.items_to_store:
            yield item
        for req in decision.next_requests:
            yield req
        if decision.need_stop:
            raise CloseSpider()

    def closed(self, reason):
        self.decision_function.finalize()
