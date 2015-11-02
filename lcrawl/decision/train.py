import os, logging, pickle
from unicodecsv import DictWriter

from scrapy.http import Request

from lcrawl.decision.base import BaseDecisionFunction, Decision
from lcrawl.utils import norm_url


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
            result["LABEL__%s" % label] = 1
        return result


UNKNOWN_LABEL = 'UNKNOWN'
UNKNOWN_LABELS = frozenset([UNKNOWN_LABEL])


TEMP_DATA_FILENAME = "temp.p"
PAGES_DATA_FILENAME = "pages.csv"
TRANSITIONS_DATA_FILENAME = "transitions.csv"


class CollectTrainData(BaseDecisionFunction):
    def __init__(self, sites_dir, out_dir, *args, **kwargs):
        self.sites = load_descriptions_from_dir(sites_dir)
        self.saved_urls = set()
        self.requested_pages = set()
        self.out_dir = out_dir
        self.temp_data_fpath = os.path.join(self.out_dir, TEMP_DATA_FILENAME)
        self.temp_data_file = open(self.temp_data_fpath, 'w')
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
        page = TrainPageInfo(response.url,
                             site,
                             response.meta['lcrawl.labels'],
                             page_features,
                             transitions)
        pickle.dump(page, self.temp_data_file)
        if already_saved or not response.request.url in self.pages_to_visit:
            next_requests = []
        else:
            next_requests = [Request(trans.to_url,
                                     meta = {
                                             'lcrawl.site' : site,
                                             'lcrawl.labels' : trans.labels
                                             })
                             for trans in transitions
                             if not trans.to_url in self.requested_pages]
        self.requested_pages.update(r.url for r in next_requests)
        return Decision(next_requests, [], False)

    def finalize(self):
        if self.finalized:
            return
        self.finalized = True

        self.temp_data_file.close()

        convert_pickled_pages_to_csv_dataset(self.temp_data_fpath,
                                             os.path.join(self.out_dir,
                                                          PAGES_DATA_FILENAME),
                                             os.path.join(self.out_dir,
                                                          TRANSITIONS_DATA_FILENAME))


def convert_pickled_pages_to_csv_dataset(in_file, out_pages_fpath, out_transitions_fpath, delete_in_file = True):
    pages_columns = set()
    transitions_columns = set()
    
    with open(in_file, 'r') as inf:
        while True:
            try:
                page = pickle.load(inf)
                pages_columns.update(page.as_dict().viewkeys())
                for trans in page.transitions:
                    transitions_columns.update(trans.as_dict({ "FROM_LABEL__%s" % l : 1
                                                              for l in page.labels }).viewkeys())
            except EOFError:
                break

    with open(out_pages_fpath, 'w') as pages_f, \
        open(out_transitions_fpath, 'w') as trans_f:
        pages_writer = DictWriter(pages_f,
                                  sorted(pages_columns),
                                  encoding = 'utf8')
        pages_writer.writeheader()
        trans_writer = DictWriter(trans_f,
                                  sorted(transitions_columns),
                                  encoding = 'utf8')
        trans_writer.writeheader()
        with open(in_file, 'r') as inf:
            while True:
                try:
                    page = pickle.load(inf)
                    pages_writer.writerow(page.as_dict())
                    for trans in page.transitions:
                        trans_writer.writerow(trans.as_dict({ "FROM_LABEL__%s" % l : 1
                                                             for l in page.labels }))
                except EOFError:
                    break

    if delete_in_file:
        os.remove(in_file)
