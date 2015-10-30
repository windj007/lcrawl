import json, os


def load_json(filename):
    with open(filename, 'r') as f:
        return json.loads(f)


def load_config(filename):
    conf = load_json(filename)
    parent_filename = conf.get('PARENT_CONFIG', None)
    if not parent_filename is None:
        parent_filename = os.path.join(os.path.dirname(filename),
                                       parent_filename)
        parent_conf = load_config(parent_filename)
        parent_conf.update(conf)
        conf = parent_conf
    return conf


def ensure_str(obj):
    if isinstance(obj, str):
        return obj
    if isinstance(obj, unicode):
        return obj.encode('utf8')
    return str(obj)


def load_obj(classname):
    module_path, _, cls = ensure_str(classname).rpartition('.')
    assert module_path, 'Could not import class from the global scope'
    mod = __import__(module_path, fromlist=[cls])
    return getattr(mod, cls)


def build_object(classname, *args, **kwargs):
    return load_obj(classname)(*args, **kwargs)


def load_obj_and_call(d):
    return load_obj(d['constructor'])(*d.get('args', []), **d.get('kwargs', {}))


class ChainException(Exception):
    def __init__(self, exceptions):
        self.exceptions = exceptions
    
    def __str__(self):
        return 'Raised exceptions: %s' % '; '.join(map(str, self.exceptions))


class FirstCaller(object):
    def __init__(self, functions):
        self.functions = functions

    def __call__(self, *args, **kwargs):
        exceptions = []
        for func in self.functions:
            try:
                return func(*args, **kwargs)
            except Exception as ex:
                exceptions.append(ex)
        raise ChainException


class DictUnion(object):
    def __init__(self, functions):
        self.functions = functions

    def __call__(self, *args, **kwargs):
        result = {}
        for func in self.functions:
            result.update(func(*args, **kwargs))
        return result


def load_callable_chain(dict_list, chain_cls):
    return chain_cls(load_obj_and_call(d) for d in dict_list)
