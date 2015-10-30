from scrapy.http import Request

from lcrawl.utils import norm_url


class Decision(object):
    def __init__(self, next_requests, items_to_store, need_stop):
        self.next_requests = next_requests
        self.items_to_store = items_to_store
        self.need_stop = need_stop


class BaseDecisionFunction(object):
    def __init__(self, *args, **kwargs):
        self.args = args
        self.kwargs = kwargs

    def get_initial_requests(self):
        return []

    def get_initial_state(self, url):
        return 

    def decide(self, state, page_features, transitions):
        return Decision([], [], True)

    def finalize(self):
        pass


class DTWithSeeds(object):
    def __init__(self, *args, **kwargs):
        self.seeds = kwargs.pop('SEEDS', [])
        self.seed_files = kwargs.pop('SEED_FILES', [])
        super(DTWithSeeds, self).__init__(*args, **kwargs)
        
    def get_initial_requests(self):
        seeds = set(self.seeds)
        for fname in self.seed_files:
            with open(fname, 'r') as f:
                seeds.update(l.strip() for l in f)
        for seed in seeds:
            url, domain = norm_url(seed)
            yield Request(url,
                          meta = {
                                  'lcrawl.labels' : self.get_initial_state(url)
                                  })
