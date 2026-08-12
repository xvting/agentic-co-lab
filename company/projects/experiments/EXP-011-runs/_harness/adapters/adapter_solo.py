"""EXP-011 adapter · inventory_solo（Inventory: register_sku/receive/ship/reserve/release/set_threshold/low_stock_skus/total_stock/available_stock）"""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "inventory_solo"))
from inventory import (Inventory, SkuNotFoundError, InsufficientStockError,
                       ReservationExceededError, ReleaseExceededError, SkuAlreadyExistsError)

_inv = Inventory()


def _ensure(sku):
    try:
        _inv.register_sku(sku)
    except SkuAlreadyExistsError:
        pass


def add(sku, qty):
    if isinstance(qty, bool) or not isinstance(qty, int) or qty <= 0:
        raise ValueError("qty must be positive int")
    _ensure(sku)
    _inv.receive(sku, qty)


def deduct(sku, qty):
    try:
        _inv.ship(sku, qty)
        return "ok"
    except SkuNotFoundError:
        return "unknown"
    except InsufficientStockError:
        return "insufficient"


def stock(sku):
    try:
        return _inv.total_stock(sku)
    except SkuNotFoundError:
        return None


def available(sku):
    try:
        return _inv.available_stock(sku)
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
    return _inv.low_stock_skus()
