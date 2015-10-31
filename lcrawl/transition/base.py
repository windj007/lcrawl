from urlparse import urlparse

from lcrawl.loading import load_obj_and_call


class Transition(object):
    def __init__(self, url, labels, features):
        self.url = url
        self.labels = labels
        self.features = features


class PluggableTransitionExtractorMixin(object):
    def __init__(self, *args, **kwargs):
        self.functions = [load_obj_and_call(d) for d in
                          kwargs.get('TRANSITION_PROCESSORS', [])]

    def get_transition(self, response, link_obj):
        result = super(PluggableTransitionExtractorMixin, self).get_transition(response,
                                                                               link_obj)
        for func in self.functions:
            result = func(response, link_obj, result)
            if result is None:
                break
        return result


class NormalizeUrls(object):
    def __call__(self, response, a, result):
        result.url = response.urljoin(result.url) 
        return result


class RestrictSameDomain(object):
    def __call__(self, response, a, result):
        req_domain = urlparse(response.request.url).hostname
        resp_domain = urlparse(result.url)
        return result if req_domain == resp_domain else None
