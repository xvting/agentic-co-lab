import time


class TTLCache:
    def __init__(self, capacity: int = 128):
        self.capacity = max(1, int(capacity))
        self._data = {}
        self._order = {}
        self._clock = 0

    def _expire_key(self, key):
        if key not in self._data:
            return
        value, expire_at = self._data[key]
        if expire_at is not None and time.monotonic() >= expire_at:
            del self._data[key]
            del self._order[key]

    def set(self, key, value, ttl_seconds: float = None):
        expire_at = None if ttl_seconds is None else time.monotonic() + ttl_seconds
        if key in self._data:
            self._data[key] = (value, expire_at)
            self._order[key] = self._clock
            self._clock += 1
            return
        if len(self._data) >= self.capacity:
            for k in list(self._data):
                if len(self._data) < self.capacity:
                    break
                self._expire_key(k)
            if len(self._data) >= self.capacity:
                lru_key = min(self._order, key=self._order.get)
                del self._data[lru_key]
                del self._order[lru_key]
        self._data[key] = (value, expire_at)
        self._order[key] = self._clock
        self._clock += 1

    def get(self, key):
        if key not in self._data:
            return None
        value, expire_at = self._data[key]
        if expire_at is not None and time.monotonic() >= expire_at:
            del self._data[key]
            del self._order[key]
            return None
        self._order[key] = self._clock
        self._clock += 1
        return value
