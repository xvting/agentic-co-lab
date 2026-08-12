"""EXP-011 adapter · inventory_arch（Inventory: add_stock/withdraw/reserve/release/set_low_stock_threshold/get_stock/get_low_stock_skus）"""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "inventory_arch"))
from inventory import (Inventory, SKUNotFoundError, InsufficientStockError, ReservationError)

_inv = Inventory()


def add(sku, qty):
    if isinstance(qty, bool) or not isinstance(qty, int) or qty <= 0:
        raise ValueError("qty must be positive int")
    _inv.add_stock(sku, qty)


def deduct(sku, qty):
    try:
        _inv.withdraw(sku, qty)
        return "ok"
    except SKUNotFoundError:
        return "unknown"
    except InsufficientStockError:
        return "insufficient"


def stock(sku):
    try:
        return _inv.get_stock(sku).total
    except SKUNotFoundError:
        return None


def available(sku):
    try:
        return _inv.get_stock(sku).available
    except SKUNotFoundError:
        return None


def reserve(sku, qty):
    try:
        _inv.reserve(sku, qty)
        return "ok"
    except SKUNotFoundError:
        return "unknown"
    except InsufficientStockError:
        return "insufficient"


def release(sku, qty):
    try:
        _inv.release(sku, qty)
        return "ok"
    except SKUNotFoundError:
        return "unknown"
    except ReservationError:
        return "invalid"


def set_threshold(sku, qty):
    try:
        _inv.set_low_stock_threshold(sku, qty)
        return "ok"
    except SKUNotFoundError:
        return "unknown"


def low_stock():
    return _inv.get_low_stock_skus()
