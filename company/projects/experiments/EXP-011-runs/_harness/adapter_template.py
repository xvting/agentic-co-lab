"""EXP-011 adapter 模板 · 每解一份（评测方撰写，只使用解的公开 API）

复制本文件为 adapter_<tag>.py，按解 USAGE.md 实现 canonical 函数。
禁止：改动解代码、访问解内部下划线成员；只能通过解的公开接口操作。

canonical 约定（与 test_suite_inventory_api.py 一致）：
    add(sku, qty)            -> None；qty<=0 抛 ValueError
    deduct(sku, qty)         -> "ok" | "insufficient" | "unknown"
    stock(sku)               -> int | None
    available(sku)           -> int | None
    reserve(sku, qty)        -> "ok" | "insufficient" | "unknown"
    release(sku, qty)        -> "ok" | "invalid" | "unknown"
    set_threshold(sku, qty)  -> "ok" | "unknown"
    low_stock()              -> list[str]

示例（假设解暴露 Inventory 类，方法 add/deduct/stock/available/reserve/release/
set_threshold/low_stock，未知 SKU 抛 KeyError，库存不足返回 False 或抛自定义异常——
请按解的实际情况改写，不限于此示例）：
"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)) + "/../inventory_solo")
from inventory import Inventory  # 改为解的模块导入方式

_inv = Inventory()

def add(sku, qty):
    if qty <= 0:
        raise ValueError("qty must be positive")
    _inv.add(sku, qty)

def deduct(sku, qty):
    try:
        ok = _inv.deduct(sku, qty)
    except KeyError:
        return "unknown"
    return "ok" if ok else "insufficient"

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
        ok = _inv.reserve(sku, qty)
    except KeyError:
        return "unknown"
    return "ok" if ok else "insufficient"

def release(sku, qty):
    try:
        ok = _inv.release(sku, qty)
    except KeyError:
        return "unknown"
    return "ok" if ok else "invalid"

def set_threshold(sku, qty):
    try:
        _inv.set_threshold(sku, qty)
    except KeyError:
        return "unknown"
    return "ok"

def low_stock():
    return _inv.low_stock()
