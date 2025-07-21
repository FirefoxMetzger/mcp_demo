import time

# super epic in-process NoSQL database
# (aka poor mans redis)
class IPDB:
    def __init__(self, lifetime: int):
        self.db = {}
        self.lifetime = lifetime

    def __getitem__(self, key):
        value, expiry = self.db[key]
        if time.time() > expiry:
            raise KeyError(f"Key {key} has expired.")
        return value

    def __setitem__(self, key, value):
        # occasionally clean up stale items to avoid memory leaks
        if len(self.db) > 100000:
            current_time = time.time()
            self.db = {k: v for k, v in self.db.items() if v[1] > time.time()}

        self.db[key] = (value, time.time() + self.lifetime)

    def __delitem__(self, key):
        del self.db[key]
