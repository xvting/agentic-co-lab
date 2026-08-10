from collections import OrderedDict
import time


class TTLCache:
    def __init__(self, capacity: int = 128):
        self.capacity = capacity
        self._data = OrderedDict()

    def set(self, key, value, ttl_seconds: float = None):
        if key in self._data:
            del self._data[key]
        elif len(self._data) >= self.capacity:
            self._purge_expired()
            if len(self._data) >= self.capacity:
                self._data.popitem(last=False)
        expire_at = None if ttl_seconds is None else time.monotonic() + ttl_seconds
        self._data[key] = (value, expire_at)

    def get(self, key):
        entry = self._data.get(key)
        if entry is None:
            return None
        value, expire_at = entry
        if expire_at is not None and time.monotonic() >= expire_at:
            del self._data[key]
            return None
        self._data.move_to_end(key)
        return value

    def _purge_expired(self):
        now = time.monotonic()
        for key in list(self._data):
            _, expire_at = self._data[key]
            if expire_at is not None and now >= expire_at:
                del self._data[key]
