from urlparse import urlparse

from lcrawl.loading import load_obj_and_call


class Transition(object):
    def __init__(self, from_url, to_url, labels, features):
        self.from_url = from_url
        self.to_url = to_url
        self.labels = labels
        self.features = features

    def as_dict(self, base = {}):
        base.update(self.features)
        base['FROM_URL'] = self.from_url
        base['TO_URL'] = self.to_url
        for l in self.labels:
            base["LABEL__%s" % l] = 1.0
        return base


class PluggableTransitionExtractorMixin(object):
    def __init__(self, *args, **kwargs):
        self.functions = [load_obj_and_call(d) for d in
                          kwargs.get('TRANSITION_PROCESSORS', [])]

    def get_transition(self, response, link_obj):
        result = super(PluggableTransitionExtractorMixin, self).get_transition(response,
                                                                               link_obj)
        for func in self.functions:
            if result is None:
                break
            result = func(response, link_obj, result)
        return result


class NormalizeUrls(object):
    def __call__(self, response, a, result):
        result.to_url = response.urljoin(result.to_url) 
        return result


class RestrictSameDomain(object):
    def __call__(self, response, a, result):
        req_domain = urlparse(response.from_url).hostname
        resp_domain = urlparse(result.to_url)
        return result if req_domain == resp_domain else None
