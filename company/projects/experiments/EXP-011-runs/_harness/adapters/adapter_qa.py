"""EXP-011 adapter · inventory_qa（Inventory: receive/issue/reserve/release/set_threshold/low_stock/get）"""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "inventory_qa"))
from inventory import (Inventory, SkuNotFoundError, InsufficientStockError,
                       ReservationExceededError, ReleaseExceededError)

_inv = Inventory()


def add(sku, qty):
    if isinstance(qty, bool) or not isinstance(qty, int) or qty <= 0:
        raise ValueError("qty must be positive int")
    _inv.receive(sku, qty)


def deduct(sku, qty):
    try:
        _inv.issue(sku, qty)
        return "ok"
    except SkuNotFoundError:
        return "unknown"
    except InsufficientStockError:
        return "insufficient"


def stock(sku):
    try:
        return _inv.get(sku).total
    except SkuNotFoundError:
        return None


def available(sku):
    try:
        return _inv.get(sku).available
    except SkuNotFoundError:
        return None


def reserve(sku, qty):
    try:
        _inv.reserve(sku, qty)
        return "ok"
    except SkuNotFoundError:
        return "unknown"
    except ReservationExceededError:
        return "insufficient"


def release(sku, qty):
    try:
        _inv.release(sku, qty)
        return "ok"
    except SkuNotFoundError:
        return "unknown"
    except ReleaseExceededError:
        return "invalid"


def set_threshold(sku, qty):
    try:
        _inv.set_threshold(sku, qty)
        return "ok"
    except SkuNotFoundError:
        return "unknown"


def low_stock():
    return _inv.low_stock()
