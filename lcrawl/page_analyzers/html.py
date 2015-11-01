from lcrawl.text import get_text_from_html_nodes


class HtmlTextExtractor(object):
    def __call__(self, response):
        html = getattr(response, 'html', None)
        if html is None:
            return {}
        return {
                'CONTENT' : get_text_from_html_nodes(html.xpath('//body')),
                'TITLE' : get_text_from_html_nodes(html.xpath('//head/title')),
                'META_DESCRIPTION' : self._get_meta_value(html, 'description'),
                'META_KEYWORDS' : self._get_meta_value(html, 'keywords')
                }

    def _get_meta_value(self, html, name):
        upper = name.upper()
        lower = name.lower()
        return ' '.join(html.xpath('//head/meta[contains(translate(@name, "%s", "%s"), "%s")]/@content' % (upper,
                                                                                                           lower,
                                                                                                           lower)))
