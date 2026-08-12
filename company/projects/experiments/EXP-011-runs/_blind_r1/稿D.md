# 稿D · USAGE

# inventory 模块使用说明

## 接口

```python
inv = Inventory()

inv.restock(sku: str, quantity: int)              # 入库；SKU 不存在时自动创建
inv.withdraw(sku: str, quantity: int)             # 出库；仅可用库存充足时成功
inv.reserve(sku: str, quantity: int)              # 预留；不得超过可用库存
inv.release(sku: str, quantity: int)              # 释放；不得超过已预留量
inv.set_threshold(sku: str, threshold: int|None)  # 设置/清除最低库存阈值
inv.low_stock_skus() -> list[str]                 # 可用库存低于阈值的 SKU 列表
inv.get_stock(sku) -> StockInfo                   # 查询 total/reserved/available
inv.has_sku(sku) -> bool                          # SKU 是否存在
```

`StockInfo` 为命名元组，字段：`total`(总库存)、`reserved`(已预留)、`available`(可用库存=总−预留)。

## 错误语义（按异常类型区分，全部继承 `InventoryError`）

| 异常 | 触发条件 |
| --- | --- |
| `InvalidQuantityError` | 数量不是正整数（≤0、非 int、bool），或阈值为负/非 int |
| `SkuNotFoundError` | 查询/出库/预留/释放/设阈值时 SKU 不存在 |
| `InsufficientStockError` | 出库或预留超过可用库存（绝不产生负库存/超卖） |
| `ReleaseExceedsReservedError` | 释放量超过已预留量 |

调用方可 `except InventoryError` 统一兜底，再按具体类型分支处理。

## 最小示例

```python
from inventory import Inventory

inv = Inventory()
inv.restock("SKU-A", 100)
inv.withdraw("SKU-A", 30)
inv.reserve("SKU-A", 20)
print(inv.get_stock("SKU-A"))  # StockInfo(total=70, reserved=20, available=50)
```

## 关键设计决策

- 数据模型：SKU 到状态对象的字典，状态含总库存、已预留、阈值，可用库存恒为总减预留，所有变更在锁内完成以维持不变量。
- 锁策略：单一可重入 `threading.RLock` 串行化全部读写，牺牲部分并行度换取简洁与正确。
- 语义选择：入库自动建档；出库与预留只动用可用库存；低库存按可用库存判断。

# 稿D · 模块源码

```python
"""inventory.py — 库存管理模块（仅标准库，线程安全）。

设计要点：
- 数据模型：{SKU: _SkuState}，状态含 total(总库存)、reserved(已预留)、threshold(阈值)。
- 可用库存 available = total - reserved，任何变更都在全局可重入锁内完成，
  保证并发下不丢更新、不超卖、不出现负库存。
- 错误通过自定义异常类型区分：InvalidQuantityError / SkuNotFoundError /
  InsufficientStockError / ReleaseExceedsReservedError，全部继承 InventoryError。
"""

from __future__ import annotations

import threading
from collections import namedtuple

__all__ = [
    "Inventory",
    "InventoryError",
    "InvalidQuantityError",
    "SkuNotFoundError",
    "InsufficientStockError",
    "ReleaseExceedsReservedError",
    "StockInfo",
]

StockInfo = namedtuple("StockInfo", ("total", "reserved", "available"))


class InventoryError(Exception):
    """库存模块所有可预期错误的基类。"""


class InvalidQuantityError(InventoryError):
    """数量非法：不是正整数（阈值为非负整数或 None）。"""


class SkuNotFoundError(InventoryError):
    """SKU 不存在。"""


class InsufficientStockError(InventoryError):
    """可用库存不足，无法出库或预留（不产生负库存/超卖）。"""


class ReleaseExceedsReservedError(InventoryError):
    """释放量超过已预留量。"""


class _SkuState:
    __slots__ = ("total", "reserved", "threshold")

    def __init__(self, total: int = 0, reserved: int = 0, threshold=None) -> None:
        self.total = total
        self.reserved = reserved
        self.threshold = threshold

    @property
    def available(self) -> int:
        return self.total - self.reserved


class Inventory:
    """线程安全的库存管理器，按 SKU 独立维护库存。"""

    def __init__(self) -> None:
        self._lock = threading.RLock()
        self._skus: dict[str, _SkuState] = {}

    # ---- 内部工具 ----

    def _validate_quantity(self, value, what: str) -> None:
        if isinstance(value, bool) or not isinstance(value, int) or value <= 0:
            raise InvalidQuantityError(f"{what}必须为正整数，收到：{value!r}")

    def _require(self, sku: str) -> _SkuState:
        state = self._skus.get(sku)
        if state is None:
            raise SkuNotFoundError(f"SKU 不存在：{sku!r}")
        return state

    # ---- 公开操作 ----

    def restock(self, sku: str, quantity: int) -> None:
        """入库：增加某 SKU 的总库存；SKU 不存在时自动创建。"""
        self._validate_quantity(quantity, "入库数量")
        with self._lock:
            state = self._skus.get(sku)
            if state is None:
                state = self._skus[sku] = _SkuState()
            state.total += quantity

    def withdraw(self, sku: str, quantity: int) -> None:
        """出库：扣减某 SKU 的总库存；仅可用库存充足时成功，否则抛 InsufficientStockError。"""
        self._validate_quantity(quantity, "出库数量")
        with self._lock:
            state = self._require(sku)
            if state.available < quantity:
                raise InsufficientStockError(
                    f"SKU {sku!r} 可用库存不足：需 {quantity}，可用 {state.available}"
                )
            state.total -= quantity

    def reserve(self, sku: str, quantity: int) -> None:
        """预留：占用可用库存（防超卖）；预留量不得超过可用库存。"""
        self._validate_quantity(quantity, "预留数量")
        with self._lock:
            state = self._require(sku)
            if state.available < quantity:
                raise InsufficientStockError(
                    f"SKU {sku!r} 可用库存不足：需预留 {quantity}，可用 {state.available}"
                )
            state.reserved += quantity

    def release(self, sku: str, quantity: int) -> None:
        """释放：归还已预留量；释放量不得超过已预留量。"""
        self._validate_quantity(quantity, "释放数量")
        with self._lock:
            state = self._require(sku)
            if quantity > state.reserved:
                raise ReleaseExceedsReservedError(
                    f"SKU {sku!r} 释放量 {quantity} 超过已预留量 {state.reserved}"
                )
            state.reserved -= quantity

    def set_threshold(self, sku: str, threshold) -> None:
        """设置最低库存阈值；threshold=None 表示清除阈值。阈值为非负整数。"""
        if threshold is not None:
            if isinstance(threshold, bool) or not isinstance(threshold, int) or threshold < 0:
                raise InvalidQuantityError(f"阈值必须为非负整数或 None，收到：{threshold!r}")
        with self._lock:
            state = self._require(sku)
            state.threshold = threshold

    def low_stock_skus(self) -> list:
        """返回可用库存低于阈值的 SKU 列表（未设阈值的 SKU 不参与）。"""
        with self._lock:
            return [
                sku
                for sku, state in self._skus.items()
                if state.threshold is not None and state.available < state.threshold
            ]

    def get_stock(self, sku: str) -> StockInfo:
        """查询某 SKU 的总库存/已预留/可用库存；SKU 不存在时抛 SkuNotFoundError。"""
        with self._lock:
            state = self._require(sku)
            return StockInfo(state.total, state.reserved, state.available)

    def has_sku(self, sku: str) -> bool:
        """SKU 是否存在（与 get_stock 不同，不存在时返回 False 而非抛错）。"""
        with self._lock:
            return sku in self._skus
```
