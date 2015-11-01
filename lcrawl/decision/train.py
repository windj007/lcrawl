import os, logging
from collections import defaultdict
from pandas import DataFrame

from scrapy.http import Request

from lcrawl.decision.base import BaseDecisionFunction, Decision
from lcrawl.utils import norm_url
from lcrawl.loading import save_json


logger = logging.getLogger()


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

    def as_dict(self):
        result = dict(**self.page_features)
        result['SITE'] = self.site
        result['URL'] = self.url
        for label in self.labels:
            result[label] = 1
        return result


UNKNOWN_LABEL = 'UNKNOWN'
UNKNOWN_LABELS = frozenset([UNKNOWN_LABEL])


PAGES_DATA_FILENAME = "pages.csv"
TRANSITIONS_DATA_FILENAME = "transitions.csv"


class CollectTrainData(BaseDecisionFunction):
    def __init__(self, sites_dir, out_dir, *args, **kwargs):
        self.sites = load_descriptions_from_dir(sites_dir)
        self.saved_pages = []
        self.saved_urls = set()
        self.requested_pages = set()
        self.out_dir = out_dir
        self.finalized = False

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
        already_saved = response.url in self.saved_urls
        self.saved_urls.add(response.url)
        transitions = list(transitions)
        for trans in transitions:
            trans.labels = self.pages_to_visit.get(trans.to_url, UNKNOWN_LABELS)
        self.saved_pages.append(TrainPageInfo(response.url,
                                              site,
                                              response.meta['lcrawl.labels'],
                                              page_features,
                                              transitions))
        if already_saved:
            next_requests = []
        else:
            next_requests = (Request(trans.to_url,
                                     meta = {
                                             'lcrawl.site' : site,
                                             'lcrawl.labels' : trans.labels
                                             })
                             for trans in transitions
                             if not trans.to_url in self.requested_pages)
        return Decision(next_requests, [], False)

    def finalize(self):
        if self.finalized:
            return
        self.finalized = True

        pages_fpath = os.path.join(self.out_dir, PAGES_DATA_FILENAME)
        pages_data = DataFrame(data = [p.as_dict() for p in self.saved_pages])
        pages_data.to_csv(pages_fpath, encoding = 'utf8')

        transitions_fpath = os.path.join(self.out_dir, TRANSITIONS_DATA_FILENAME)
        transitions_data = DataFrame(data = [t.as_dict({ "FROM_LABELS" : p.labels })
                                             for p in self.saved_pages
                                             for t in p.transitions])
        transitions_data.to_csv(transitions_fpath, encoding = 'utf8')
