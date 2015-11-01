import logging
from StringIO import StringIO
from lxml.html import HTMLParser, parse
from scrapy.http import HtmlResponse


logger = logging.getLogger()

_HTML_PARSER = HTMLParser(encoding = 'utf8')

class HtmlParser(object):
    def __call__(self, response):
        if not isinstance(response, HtmlResponse):
            return
        response.html = parse(StringIO(response.body_as_unicode().encode('utf8')),
                              _HTML_PARSER)

