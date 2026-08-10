import time
from collections import OrderedDict


class TTLCache:
    def __init__(self, capacity: int = 128):
        self.capacity = max(0, int(capacity))
        self._cache = OrderedDict()  # key -> value, insertion order == LRU order
        self._expires = {}           # key -> monotonic deadline, or None for no expiry

    def set(self, key, value, ttl_seconds: float = None):
        if self.capacity == 0:
            return
        now = time.monotonic()
        if key in self._cache:
            del self._cache[key]
        self._cache[key] = value
        self._expires[key] = now + ttl_seconds if ttl_seconds is not None else None
        self._purge_expired(now)
        while len(self._cache) > self.capacity:
            oldest, _ = next(iter(self._cache.items()))
            del self._cache[oldest]
            self._expires.pop(oldest, None)

    def get(self, key):
        now = time.monotonic()
        if key not in self._cache:
            return None
        deadline = self._expires.get(key)
        if deadline is not None and now >= deadline:
            del self._cache[key]
            self._expires.pop(key, None)
            return None
        self._cache.move_to_end(key)
        return self._cache[key]

    def __len__(self):
        self._purge_expired(time.monotonic())
        return len(self._cache)

    def _purge_expired(self, now):
        expired = [
            k for k, deadline in self._expires.items()
            if deadline is not None and now >= deadline
        ]
        for k in expired:
            del self._cache[k]
            self._expires.pop(k, None)
