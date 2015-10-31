from StringIO import StringIO
from lxml.html import HTMLParser, parse
from scrapy.http import HtmlResponse


class HtmlParser(object):
    def __call__(self, response):
        if not isinstance(response, HtmlResponse):
            return
        response.html = parse(StringIO(response.body),
                              HTMLParser(encoding = response.encoding))

