import os
from collections import defaultdict

from scrapy.http import Request

from lcrawl.decision.base import BaseDecisionFunction, Decision
from lcrawl.utils import norm_url


class SiteDescription(object):
    def __init__(self, pages, filename):
        self.pages = pages
        self.filename = filename

    @classmethod
    def load_from_txt(cls, filename):
        with open(filename, 'r') as f:
            return cls([(labels.split(','), norm_url(url)[0])
                        for labels, url
                        in (l.strip().split(' ') for l in f)],
                       filename)


def load_descriptions_from_dir(dirname):
    for fname in os.listdir(dirname):
        fpath = os.path.join(dirname, fname)
        if not os.path.isfile(fpath):
            continue
        yield SiteDescription.load_from_txt(fpath)


class TrainPageInfo(object):
    def __init__(self, url, site, labels, page_features, transitions):
        self.url = url
        self.site = site
        self.labels = labels
        self.page_features = page_features
        self.transitions = transitions


UNKNOWN_LABEL = 'UNKNOWN'
UNKNOWN_LABELS = frozenset([UNKNOWN_LABEL])


class BaseTrainDF(BaseDecisionFunction):
    def __init__(self, sites_dir, out_dir, *args, **kwargs):
        self.sites = load_descriptions_from_dir(sites_dir)
        self.saved_pages = defaultdict(list)
        self.requested_pages = set()
        self.out_dir = out_dir

    def get_initial_requests(self):
        self.pages_to_visit = {}
        for site in self.sites:
            for labels, url in site.pages:
                self.pages_to_visit[url] = labels
                self.requested_pages.add(url)
                yield Request(url,
                              meta = {
                                      'lcrawl.site' : site.filename,
                                      'lcrawl.labels' : labels
                                      })

    def decide(self, response, page_features, transitions):
        site = response.meta['lcrawl.site']
        already_saved = response.url in self.saved_pages
        self.saved_pages[response.url].append(TrainPageInfo(response.url,
                                                            site,
                                                            response.meta['lcrawl.labels'],
                                                            page_features,
                                                            transitions))
        if already_saved:
            next_requests = []
        else:
            next_requests = (Request(trans.url,
                                     meta = {
                                             'lcrawl.site' : site,
                                             'lcrawl.labels' : self.pages_to_visit.get(trans.url,
                                                                                       UNKNOWN_LABELS)
                                             })
                             for trans in transitions
                             if not trans.url in self.requested_pages)
        return Decision(next_requests, [], True)

    def finalize(self):
        pass
