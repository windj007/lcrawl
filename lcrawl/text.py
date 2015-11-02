import itertools, re
from nltk.tokenize import RegexpTokenizer
from nltk.stem import SnowballStemmer
from langid.langid import classify as get_lang


def get_text_from_html(root):
    result = ' '.join(root.xpath('./text() | '
                                 './/*[not(starts-with(local-name(), "script")) '
                                 'and not(starts-with(local-name(), "style"))]/text()'))
    if isinstance(result, unicode):
        return result.encode('utf8')
    return result


def get_text_from_html_nodes(nodes):
    return ' '.join(get_text_from_html(n) for n in nodes)


_WORD_DIV_RE = re.compile(r'([^\W\d_]+)-\n\s*([^\W\d_]+)', re.I) # | re.U)
_WORD_DIV_SUB = r'\1\2'
def remove_word_divisions(text):
    return _WORD_DIV_RE.sub(_WORD_DIV_SUB, text)


_STEMMERS_BY_LANG = {
                     'en' : SnowballStemmer('english').stem,
                     'ru' : SnowballStemmer('russian').stem
                     }

_DEFAULT_STEMMER = _STEMMERS_BY_LANG['ru']
_TOKENIZE_IMPL = RegexpTokenizer(r'\w+|[^\w\s]+', flags = re.DOTALL | re.MULTILINE).tokenize

def _filter_tokens(tok):
    return len(tok) > 2 and tok.isalnum()


class _StemConvert(object):
    def __init__(self, stem):
        self.stem = stem
    def __call__(self, token):
        return self.stem(token).encode('utf8')


def parse_string(txt, default_lang):
    txt = txt.strip()
    if not txt:
        return []
    lang = get_lang(txt)[0]
    tokens = _TOKENIZE_IMPL(txt.lower().decode('utf8'))
    filtered_tokens = itertools.ifilter(_filter_tokens, tokens)
    stem = _StemConvert(_STEMMERS_BY_LANG.get(lang, _STEMMERS_BY_LANG[default_lang]))
    stemmed_tokens = map(stem, filtered_tokens)
    return stemmed_tokens
