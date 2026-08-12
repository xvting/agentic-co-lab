"""EXP-011 评测装置校准用参考实现（校准 only，明确不计入基线）。

用途：验证 test_suite_inventory_api.py 可运行、断言口径自洽。
绝不作为实验稿、不进入盲评、不参与任何增益计算。
"""
import threading


class Inventory:
    """线程安全的库存管理（RLock 细粒度保护，含预留/阈值）。"""

    def __init__(self):
        self._lock = threading.RLock()
        self._stock = {}
        self._reserved = {}
        self._threshold = {}

    @staticmethod
    def _check_qty(qty):
        if isinstance(qty, bool) or not isinstance(qty, int) or qty <= 0:
            raise ValueError("qty must be a positive int")

    def _exists(self, sku):
        return sku in self._stock

    def add(self, sku, qty):
        self._check_qty(qty)
        with self._lock:
            self._stock[sku] = self._stock.get(sku, 0) + qty

    def deduct(self, sku, qty):
        self._check_qty(qty)
        with self._lock:
            if not self._exists(sku):
                raise KeyError(sku)
            if self._stock[sku] - self._reserved.get(sku, 0) < qty:
                return False
            self._stock[sku] -= qty
            return True

    def reserve(self, sku, qty):
        self._check_qty(qty)
        with self._lock:
            if not self._exists(sku):
                raise KeyError(sku)
            if self._stock[sku] - self._reserved.get(sku, 0) < qty:
                return False
            self._reserved[sku] = self._reserved.get(sku, 0) + qty
            return True

    def release(self, sku, qty):
        self._check_qty(qty)
        with self._lock:
            if not self._exists(sku):
                raise KeyError(sku)
            if self._reserved.get(sku, 0) < qty:
                return False
            self._reserved[sku] -= qty
            return True

    def stock(self, sku):
        with self._lock:
            if not self._exists(sku):
                raise KeyError(sku)
            return self._stock[sku]

    def available(self, sku):
        with self._lock:
            if not self._exists(sku):
                raise KeyError(sku)
            return self._stock[sku] - self._reserved.get(sku, 0)

    def set_threshold(self, sku, qty):
        self._check_qty(qty)
        with self._lock:
            if not self._exists(sku):
                raise KeyError(sku)
            self._threshold[sku] = qty

    def low_stock(self):
        with self._lock:
            return sorted(s for s in self._stock
                          if s in self._threshold and self._stock[s] < self._threshold[s])
