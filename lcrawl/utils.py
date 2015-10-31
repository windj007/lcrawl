from urlparse import urlparse

def norm_url(url):
    url = url.strip()
    parsed = urlparse(url)
    if not parsed.hostname():
        parsed = urlparse('http://' + url)
    return parsed.geturl(), parsed.hostname


def get_domain(url):
    return urlparse(url).hostname