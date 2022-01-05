"""
Cache Utility
"""

class Cache(object):
    """
    Caching Object
    """
    def __init__(self):
        self.reset()

    def reset(self):
        self.storage = {
                'get_current_user': [{}],
                'get_item': [{}],
                }
