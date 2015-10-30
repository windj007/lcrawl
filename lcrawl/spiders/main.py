import scrapy
from scrapy.exceptions import CloseSpider

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
                 decision_function,
                 preprocessors,
                 transition_extractors,
                 page_analyzers):
        self.decision_function = decision_function
        self.preprocessors = preprocessors
        self.transition_extractors = transition_extractors
        self.page_analyzers = page_analyzers

    @classmethod
    def from_crawler(cls, crawler):
        return cls(load_obj_and_call(crawler.settings.get('DECISION_FUNCTION')),
                   load_callable_chain(crawler.settings.get('PREPROCESSORS'),
                                       AllCaller),
                   load_callable_chain(crawler.settings.get('TRANSITION_EXTRACTORS'),
                                       CallAndChain),
                   load_callable_chain(crawler.settings.get('PAGE_ANALYZERS'),
                                       DictUnion))

    def start_requests(self):
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
            raise CloseSpider()

    def closed(self, reason):
        self.decision_function.finalize()
