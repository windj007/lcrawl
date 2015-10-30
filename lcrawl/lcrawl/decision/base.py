class Decision(object):
    def __init__(self, next_requests, items_to_store, need_stop):
        self.next_requests = next_requests
        self.items_to_store = items_to_store
        self.need_stop = need_stop


class BaseDecisionFunction(object):
    def __init__(self, *args, **kwargs):
        self.args = args
        self.kwargs = kwargs

    def get_initial_state(self):
        return None

    def decide(self, state, page_features, transitions):
        return Decision([], [], True)
