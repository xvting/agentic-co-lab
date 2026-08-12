# 稿C · USAGE

# USAGE — inventory 库存管理模块

## 接口

```python
from inventory import Inventory

inv = Inventory()
inv.register_sku("SKU-A")          # 注册 SKU
inv.receive("SKU-A", 100)          # 入库，返回操作后的可用库存
inv.ship("SKU-A", 30)              # 出库，返回操作后的可用库存
inv.reserve("SKU-A", 50)           # 预留，返回操作后的可用库存
inv.release("SKU-A", 50)           # 释放，返回操作后的可用库存
inv.set_threshold("SKU-A", 80)     # 设置最低库存阈值（非负整数）
inv.low_stock_skus()               # 总库存低于阈值的 SKU 列表
inv.total_stock("SKU-A")           # 总库存
inv.available_stock("SKU-A")       # 可用库存 = 总库存 - 已预留
inv.reserved_stock("SKU-A")        # 已预留量
inv.get_threshold("SKU-A")         # 当前阈值
inv.has_sku("SKU-A")               # 是否已注册（不抛错）
inv.skus()                         # 已注册 SKU 列表
```

## 错误语义

所有异常都是 `InventoryError` 的子类，按异常类型即可区分：

| 异常 | 触发条件 |
| --- | --- |
| `InvalidSkuError` | SKU 非字符串或空字符串 |
| `InvalidQuantityError` | 数量非正整数，或阈值非法 |
| `SkuNotFoundError` | SKU 未注册 |
| `SkuAlreadyExistsError` | 重复注册 |
| `InsufficientStockError` | 出库量超过可用库存 |
| `ReservationExceededError` | 预留量超过可用库存 |
| `ReleaseExceededError` | 释放量超过已预留量 |

「SKU 不存在」「库存不足」「参数非法」分别对应 `SkuNotFoundError`、`InsufficientStockError`、`InvalidQuantityError`，可通过 `except` 或 `type(exc)` 区分；失败操作不会改变库存。

## 最小示例

```python
from inventory import Inventory, InsufficientStockError

inv = Inventory()
inv.register_sku("SKU-A")
inv.receive("SKU-A", 100)          # 可用 100
inv.reserve("SKU-A", 50)           # 可用 50
try:
    inv.ship("SKU-A", 60)          # 60 > 50，失败
except InsufficientStockError:
    print("库存不足")
print(inv.available_stock("SKU-A"))  # 50
```

## 关键设计决策

1. 数据模型：内部维护 `SKU -> (总库存, 已预留, 阈值)` 状态字典，可用量 = 总库存 − 已预留，所有不变量在锁内保证。
2. 锁策略：单一 `threading.RLock` 串行化全部读写，更新原子、无死锁，满足并发正确性。
3. 阈值语义：总库存 < 阈值即低库存，默认阈值 0 表示不告警。

# 稿C · 模块源码

```python
# -*- coding: utf-8 -*-
"""库存管理模块（仅标准库，线程安全）。

为小型电商仓库场景提供按 SKU 的库存管理：入库、出库、预留、释放、
低库存阈值告警与并发安全保证。全部公开操作经单一可重入锁串行化，
保证更新原子、不超卖、不出现负库存。

用法::

    from inventory import Inventory

    inv = Inventory()
    inv.register_sku("SKU-A")
    inv.receive("SKU-A", 100)
    inv.ship("SKU-A", 30)
"""

from __future__ import annotations

import threading
from typing import Dict, List

__all__ = [
    "Inventory",
    "InventoryError",
    "InvalidSkuError",
    "InvalidQuantityError",
    "SkuNotFoundError",
    "SkuAlreadyExistsError",
    "InsufficientStockError",
    "ReservationExceededError",
    "ReleaseExceededError",
]


class InventoryError(Exception):
    """库存模块所有错误的基类，可用于统一捕获。"""


class InvalidSkuError(InventoryError):
    """SKU 非法：不是字符串或为空字符串。"""


class InvalidQuantityError(InventoryError):
    """数值参数非法：数量不是正整数（布尔值、非 int、<=0 均拒绝）。"""


class SkuNotFoundError(InventoryError):
    """SKU 未注册。"""


class SkuAlreadyExistsError(InventoryError):
    """SKU 已注册，不允许重复注册。"""


class InsufficientStockError(InventoryError):
    """出库量超过可用库存（含被预留部分，不发生超卖）。"""


class ReservationExceededError(InventoryError):
    """预留量超过可用库存（防超卖）。"""


class ReleaseExceededError(InventoryError):
    """释放量超过已预留量。"""


class _SkuState:
    """单个 SKU 的内部状态。"""

    __slots__ = ("total", "reserved", "threshold")

    def __init__(self) -> None:
        self.total = 0      # 总库存
        self.reserved = 0   # 已预留量
        self.threshold = 0  # 最低库存阈值（默认 0，即不告警）


class Inventory:
    """线程安全的库存管理容器。

    不变量（全部在锁内维护）：
    - 任意时刻 total >= reserved >= 0（可用库存 = total - reserved 不为负）；
    - 出库/预留都只允许扣减可用库存，杜绝超卖。
    """

    def __init__(self) -> None:
        self._lock = threading.RLock()
        self._skus: Dict[str, _SkuState] = {}

    # ------------------------------------------------------------------
    # 内部工具
    # ------------------------------------------------------------------
    @staticmethod
    def _validate_sku(sku: str) -> None:
        if not isinstance(sku, str) or sku == "":
            raise InvalidSkuError(sku)

    @staticmethod
    def _validate_quantity(quantity: int) -> None:
        if isinstance(quantity, bool) or not isinstance(quantity, int) or quantity <= 0:
            raise InvalidQuantityError(quantity)

    @staticmethod
    def _validate_threshold(threshold: int) -> None:
        if isinstance(threshold, bool) or not isinstance(threshold, int) or threshold < 0:
            raise InvalidQuantityError(threshold)

    def _state(self, sku: str) -> _SkuState:
        # 调用方须已持有 self._lock
        try:
            return self._skus[sku]
        except KeyError:
            raise SkuNotFoundError(sku) from None

    # ------------------------------------------------------------------
    # SKU 注册与查询
    # ------------------------------------------------------------------
    def register_sku(self, sku: str) -> None:
        """注册一个 SKU；重复注册抛 SkuAlreadyExistsError。"""
        self._validate_sku(sku)
        with self._lock:
            if sku in self._skus:
                raise SkuAlreadyExistsError(sku)
            self._skus[sku] = _SkuState()

    def has_sku(self, sku: str) -> bool:
        """SKU 是否已注册（不会抛错）。"""
        self._validate_sku(sku)
        with self._lock:
            return sku in self._skus

    def skus(self) -> List[str]:
        """返回全部已注册 SKU 的排序副本。"""
        with self._lock:
            return sorted(self._skus.keys())

    # ------------------------------------------------------------------
    # 出入库
    # ------------------------------------------------------------------
    def receive(self, sku: str, quantity: int) -> int:
        """入库：增加总库存，返回操作后的可用库存。"""
        self._validate_sku(sku)
        self._validate_quantity(quantity)
        with self._lock:
            st = self._state(sku)
            st.total += quantity
            return st.total - st.reserved

    def ship(self, sku: str, quantity: int) -> int:
        """出库：扣减可用库存；可用不足抛 InsufficientStockError，返回操作后的可用库存。"""
        self._validate_sku(sku)
        self._validate_quantity(quantity)
        with self._lock:
            st = self._state(sku)
            available = st.total - st.reserved
            if quantity > available:
                raise InsufficientStockError(sku, quantity, available)
            st.total -= quantity
            return st.total - st.reserved

    # ------------------------------------------------------------------
    # 预留与释放
    # ------------------------------------------------------------------
    def reserve(self, sku: str, quantity: int) -> int:
        """预留：预占可用量；超过可用库存抛 ReservationExceededError，返回操作后的可用库存。"""
        self._validate_sku(sku)
        self._validate_quantity(quantity)
        with self._lock:
            st = self._state(sku)
            available = st.total - st.reserved
            if quantity > available:
                raise ReservationExceededError(sku, quantity, available)
            st.reserved += quantity
            return st.total - st.reserved

    def release(self, sku: str, quantity: int) -> int:
        """释放：归还已预留量；超过已预留量抛 ReleaseExceededError，返回操作后的可用库存。"""
        self._validate_sku(sku)
        self._validate_quantity(quantity)
        with self._lock:
            st = self._state(sku)
            if quantity > st.reserved:
                raise ReleaseExceededError(sku, quantity, st.reserved)
            st.reserved -= quantity
            return st.total - st.reserved

    # ------------------------------------------------------------------
    # 阈值与低库存
    # ------------------------------------------------------------------
    def set_threshold(self, sku: str, threshold: int) -> None:
        """设置最低库存阈值（非负整数）；总库存 < 阈值即视为低库存。"""
        self._validate_sku(sku)
        self._validate_threshold(threshold)
        with self._lock:
            self._state(sku).threshold = threshold

    def get_threshold(self, sku: str) -> int:
        """查询 SKU 的当前阈值。"""
        self._validate_sku(sku)
        with self._lock:
            return self._state(sku).threshold

    def low_stock_skus(self) -> List[str]:
        """返回总库存低于阈值的 SKU 列表（排序）。"""
        with self._lock:
            return sorted(
                sku for sku, st in self._skus.items() if st.total < st.threshold
            )

    # ------------------------------------------------------------------
    # 库存查询
    # ------------------------------------------------------------------
    def total_stock(self, sku: str) -> int:
        """查询总库存；SKU 未注册抛 SkuNotFoundError。"""
        self._validate_sku(sku)
        with self._lock:
            return self._state(sku).total

    def reserved_stock(self, sku: str) -> int:
        """查询已预留量。"""
        self._validate_sku(sku)
        with self._lock:
            return self._state(sku).reserved

    def available_stock(self, sku: str) -> int:
        """查询可用库存 = 总库存 - 已预留。"""
        self._validate_sku(sku)
        with self._lock:
            st = self._state(sku)
            return st.total - st.reserved
```
