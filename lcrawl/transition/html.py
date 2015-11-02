import logging
from math import log1p
from collections import defaultdict

from lcrawl.transition.base import Transition, PluggableTransitionExtractorMixin
from lcrawl.text import parse_string, get_text_from_html


logger = logging.getLogger()


class BaseHtmlLinkTransitionExtractor(object):
    def __init__(self, *args, **kwargs):
        self.args = args
        self.kwargs = kwargs

    def __call__(self, response):
        html = getattr(response, 'html', None)
        if html is None:
            return
        for a in html.xpath('//body//a[@href]'):
            trans = self.get_transition(response, a)
            if not trans is None:
                yield trans

    def get_transition(self, response, a):
        href = a.get('href', None)
        return Transition(response.request.url,
                          href,
                          set(),
                          {}) if href else None


class PluggableHtmlLinkTransitionExtractor(PluggableTransitionExtractorMixin,
                                           BaseHtmlLinkTransitionExtractor):
    pass


class LinkLabelTokens(object):
    DEFAULT_LANGUAGE = 'ru'
    def __init__(self,
                 prefix = "TEXT_BOW",
                 default_language = DEFAULT_LANGUAGE):
        self.prefix = prefix
        self.default_language = default_language

    def __call__(self, response, a, result):
        text = get_text_from_html(a)
        this_features = defaultdict(float)
        norm = 0.0
        for token in parse_string(text, self.default_language):
            this_features[self.prefix + '__' + token] += 1.0
            norm += 1
        norm = log1p(norm)
        result.features.update((t, log1p(c) / norm)
                                for t, c
                                in this_features.viewitems())
        return result
