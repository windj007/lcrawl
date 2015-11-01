import base64


class ContentTypeExtractor(object):
    def __call__(self, response):
        return {
                'CONTENT_TYPE' : response.headers['content-type']
                }


class RawContentAssigner(object):
    def __call__(self, response):
        return {
                'RAW_CONTENT' : base64.encodestring(response.body)
                }
