"""EXP-011 校准 adapter（对应 reference_impl.py；仅验证套件，不计入基线）"""
import os
import sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from reference_impl import Inventory

_inv = Inventory()


def add(sku, qty):
    if qty <= 0:
        raise ValueError("qty must be positive")
    _inv.add(sku, qty)


def deduct(sku, qty):
    try:
        return "ok" if _inv.deduct(sku, qty) else "insufficient"
    except KeyError:
        return "unknown"


def stock(sku):
    try:
        return _inv.stock(sku)
    except KeyError:
        return None


def available(sku):
    try:
        return _inv.available(sku)
    except KeyError:
        return None


def reserve(sku, qty):
    try:
        return "ok" if _inv.reserve(sku, qty) else "insufficient"
    except KeyError:
        return "unknown"


def release(sku, qty):
    try:
        return "ok" if _inv.release(sku, qty) else "invalid"
    except KeyError:
        return "unknown"


def set_threshold(sku, qty):
    try:
        _inv.set_threshold(sku, qty)
        return "ok"
    except KeyError:
        return "unknown"


def low_stock():
    return _inv.low_stock()
