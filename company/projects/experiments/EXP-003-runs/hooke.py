from collections import OrderedDict
import time


class TTLCache:
    def __init__(self, capacity: int = 128):
        self.capacity = max(0, capacity)
        self._store = OrderedDict()
        self._expires = {}

    def set(self, key, value, ttl_seconds: float = None):
        if self.capacity == 0:
            return
        if key in self._store:
            del self._store[key]
        elif len(self._store) >= self.capacity:
            oldest, _ = self._store.popitem(last=False)
            self._expires.pop(oldest, None)
        self._store[key] = value
        if ttl_seconds is None:
            self._expires.pop(key, None)
        else:
            self._expires[key] = time.monotonic() + ttl_seconds

    def get(self, key):
        if key not in self._store:
            return None
        expires_at = self._expires.get(key)
        if expires_at is not None and expires_at <= time.monotonic():
            del self._store[key]
            self._expires.pop(key, None)
            return None
        self._store.move_to_end(key)
        return self._store[key]
