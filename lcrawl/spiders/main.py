import scrapy
from scrapy.exceptions import CloseSpider
from scrapy.signals import spider_closed

from lcrawl.loading import load_callable_chain, \
    load_obj_and_call, DictUnion, CallAndChain, AllCaller


def copy_meta(from_response, to_request, prefix = 'lcrawl'):
    for meta_field, meta_value in from_response.meta.viewitems():
        if not meta_field.startswith(prefix):
            continue
        if not meta_field in to_request.meta:
            to_request.meta[meta_field] = meta_value


class MainSpider(scrapy.Spider):
    name = "main"

    def __init__(self,
                 crawler,
                 decision_function,
                 preprocessors,
                 transition_extractors,
                 page_analyzers):
        self.log("Created MainSpider")
        self.crawler = crawler
        self.decision_function = decision_function
        self.preprocessors = preprocessors
        self.transition_extractors = transition_extractors
        self.page_analyzers = page_analyzers
        self.crawler.signals.connect(self.spider_closed_handler, spider_closed)

    @classmethod
    def from_crawler(cls, crawler):
        return cls(crawler,
                   load_obj_and_call(crawler.settings.get('DECISION_FUNCTION')),
                   load_callable_chain(crawler.settings.get('PREPROCESSORS'),
                                       AllCaller),
                   load_callable_chain(crawler.settings.get('TRANSITION_EXTRACTORS'),
                                       CallAndChain),
                   load_callable_chain(crawler.settings.get('PAGE_ANALYZERS'),
                                       DictUnion))

    def start_requests(self):
        self.log("Getting start requests from decision function")
        return self.decision_function.get_initial_requests()

    def parse(self, response):
        if response.status >= 400:
            return
        self.preprocessors(response)
        decision = self.decision_function.decide(response,
                                                 self.page_analyzers(response),
                                                 self.transition_extractors(response))
        for item in decision.items_to_store:
            yield item
        for req in decision.next_requests:
            yield req
        if decision.need_stop:
            self.log("Decision function said that we have to stop, stopping...")
            raise CloseSpider()

    def spider_closed_handler(self, spider, reason):
        if spider != self:
            return
        self.log("Closed called, finalizing decision function...")
        self.decision_function.finalize()
