# 稿B · USAGE

# 库存管理模块接口说明

## 模块与入口

`inventory.py` 提供线程安全的 `Inventory` 类（仅标准库）。`import inventory` 即可使用。

## 接口

```python
class Inventory:
    def add_stock(self, sku: str, quantity: int) -> None
    def withdraw(self, sku: str, quantity: int) -> None
    def reserve(self, sku: str, quantity: int) -> None
    def release(self, sku: str, quantity: int) -> None
    def set_low_stock_threshold(self, sku: str, threshold: int) -> None
    def clear_low_stock_threshold(self, sku: str) -> None
    def get_stock(self, sku: str) -> StockSnapshot  # (total, reserved, available)
    def get_low_stock_skus(self) -> list[str]
    def contains(self, sku: str) -> bool

class StockSnapshot(NamedTuple):
    total: int
    reserved: int
    available: int
```

`add_stock` 对不存在的 SKU 自动建档；出库/预留/释放/查询/设阈值对不存在的 SKU 抛 `SKUNotFoundError`。`available = total - reserved`，出库与预留只允许动用可用量，故不会超卖、不会出现负库存。低库存 = 总库存严格低于阈值（阈值 0 表示永不低库存）。

## 错误语义（按异常类型区分）

| 异常 | 触发场景 |
| --- | --- |
| `InvalidQuantityError` | 数量 ≤ 0 或非 int（含 bool）；阈值 < 0 或非 int；SKU 非字符串 |
| `SKUNotFoundError` | 对不存在的 SKU 执行出库/预留/释放/查询/设阈值 |
| `InsufficientStockError` | 出库或预留超过可用量；携带 `sku/requested/available/total/reserved/operation` 属性 |
| `ReservationError` | 释放量超过已预留量 |

四类异常互不相同，均继承 `InventoryError`，可分别 `except` 精确区分。

## 最小示例

```python
import inventory

inv = inventory.Inventory()
inv.add_stock("SKU-A", 100)   # 总/可用 = 100
inv.withdraw("SKU-A", 30)     # 总/可用 = 70
inv.reserve("SKU-A", 50)      # 可用 = 20
inv.release("SKU-A", 50)      # 可用 = 70
print(inv.get_stock("SKU-A")) # StockSnapshot(total=70, reserved=0, available=70)
```

## 关键设计决策

每个 SKU 用独立状态对象记录总库存、已预留、阈值，可用库存始终由「总 − 预留」推导，杜绝负库存。全部读写在单一可重入锁内原子完成，保证并发不丢更新、不超卖。异常按语义分层（基类加四类子异常），调用方按类型即可区分失败原因。


# 稿B · 模块源码

```python
"""库存管理模块（仅标准库，线程安全）。

领域模型：库存按 SKU 组织；每个 SKU 维护 总库存(total)、已预留(reserved)、
低库存阈值(threshold)。可用库存始终由「总库存 - 已预留」推导，任何操作都
不允许其小于 0，因此不会出现负库存，也不会超卖。

并发策略：单一可重入锁(RLock) 保护全部状态，所有「读-改-写」均在锁内原子
完成，并发入库/出库/预留/释放不丢更新、不超卖。
"""

from __future__ import annotations

import threading
from dataclasses import dataclass
from typing import Dict, List, NamedTuple, Optional

__all__ = [
    "Inventory",
    "StockSnapshot",
    "InventoryError",
    "InvalidQuantityError",
    "SKUNotFoundError",
    "InsufficientStockError",
    "ReservationError",
]


class InventoryError(Exception):
    """库存模块所有异常的共同基类；可按类型区分错误。"""


class InvalidQuantityError(InventoryError, ValueError):
    """参数非法：数量不是正整数、阈值不是非负整数、SKU 不是字符串。"""


class SKUNotFoundError(InventoryError, KeyError):
    """SKU 不存在。"""


class InsufficientStockError(InventoryError):
    """库存不足：出库超过可用库存，或预留超过可用库存（防超卖）。"""

    def __init__(self, sku, requested, available, reserved, total, operation):
        self.sku = sku
        self.requested = requested
        self.available = available
        self.reserved = reserved
        self.total = total
        self.operation = operation  # "withdraw" 或 "reserve"
        super().__init__(
            f"{operation}: sku={sku!r} 库存不足, 请求 {requested}, "
            f"可用 {available}, 总库存 {total}, 已预留 {reserved}"
        )


class ReservationError(InventoryError):
    """预留语义错误：释放量超过该 SKU 的已预留量。"""

    def __init__(self, sku, requested, reserved):
        self.sku = sku
        self.requested = requested
        self.reserved = reserved
        super().__init__(f"释放量 {requested} 超过已预留量 {reserved} (sku={sku!r})")


class StockSnapshot(NamedTuple):
    """一次查询返回的库存快照。"""

    total: int      # 总库存
    reserved: int   # 已预留
    available: int  # 可用库存 = total - reserved


@dataclass
class _SkuState:
    total: int = 0
    reserved: int = 0
    threshold: Optional[int] = None


class Inventory:
    """线程安全的库存管理聚合。

    用法：add_stock 入库（SKU 不存在时自动创建）；随后可 withdraw /
    reserve / release / 查询。对不存在的 SKU 执行出库、预留、释放、
    查询、设阈值会抛出 SKUNotFoundError。
    """

    def __init__(self) -> None:
        self._lock = threading.RLock()
        self._skus: Dict[str, _SkuState] = {}

    # ---- 参数校验 -------------------------------------------------

    @staticmethod
    def _validate_sku(sku: str) -> None:
        if not isinstance(sku, str):
            raise InvalidQuantityError(f"SKU 必须为字符串, 收到 {sku!r}")

    @staticmethod
    def _validate_positive(quantity: int, what: str) -> None:
        if isinstance(quantity, bool) or not isinstance(quantity, int) or quantity <= 0:
            raise InvalidQuantityError(f"{what}必须为正整数, 收到 {quantity!r}")

    # ---- 变更操作 -------------------------------------------------

    def add_stock(self, sku: str, quantity: int) -> None:
        """入库：增加总库存；SKU 不存在时自动创建。"""
        self._validate_sku(sku)
        self._validate_positive(quantity, "入库数量")
        with self._lock:
            state = self._skus.setdefault(sku, _SkuState())
            state.total += quantity

    def withdraw(self, sku: str, quantity: int) -> None:
        """出库：从可用库存中扣减；可用不足抛 InsufficientStockError。"""
        self._validate_sku(sku)
        self._validate_positive(quantity, "出库数量")
        with self._lock:
            state = self._require_sku(sku)
            available = state.total - state.reserved
            if available < quantity:
                raise InsufficientStockError(
                    sku, quantity, available, state.reserved, state.total, "withdraw"
                )
            state.total -= quantity

    def reserve(self, sku: str, quantity: int) -> None:
        """预留：把可用量转为已预留；可用不足抛 InsufficientStockError（防超卖）。"""
        self._validate_sku(sku)
        self._validate_positive(quantity, "预留数量")
        with self._lock:
            state = self._require_sku(sku)
            available = state.total - state.reserved
            if available < quantity:
                raise InsufficientStockError(
                    sku, quantity, available, state.reserved, state.total, "reserve"
                )
            state.reserved += quantity

    def release(self, sku: str, quantity: int) -> None:
        """释放：把已预留量返还给可用量；释放超过已预留抛 ReservationError。"""
        self._validate_sku(sku)
        self._validate_positive(quantity, "释放数量")
        with self._lock:
            state = self._require_sku(sku)
            if state.reserved < quantity:
                raise ReservationError(sku, quantity, state.reserved)
            state.reserved -= quantity

    def set_low_stock_threshold(self, sku: str, threshold: int) -> None:
        """设置低库存阈值（非负整数）；0 表示永不低库存。"""
        self._validate_sku(sku)
        if isinstance(threshold, bool) or not isinstance(threshold, int) or threshold < 0:
            raise InvalidQuantityError(f"阈值必须为非负整数, 收到 {threshold!r}")
        with self._lock:
            self._require_sku(sku).threshold = threshold

    def clear_low_stock_threshold(self, sku: str) -> None:
        """清除低库存阈值（可选操作）。"""
        self._validate_sku(sku)
        with self._lock:
            self._require_sku(sku).threshold = None

    # ---- 查询操作 -------------------------------------------------

    def get_stock(self, sku: str) -> StockSnapshot:
        """查询总库存/已预留/可用库存；SKU 不存在抛 SKUNotFoundError。"""
        self._validate_sku(sku)
        with self._lock:
            state = self._require_sku(sku)
            return StockSnapshot(state.total, state.reserved, state.total - state.reserved)

    def get_low_stock_skus(self) -> List[str]:
        """返回当前总库存低于阈值的 SKU（未设阈值的不算；按 SKU 排序）。"""
        with self._lock:
            return sorted(
                sku
                for sku, state in self._skus.items()
                if state.threshold is not None and state.total < state.threshold
            )

    def contains(self, sku: str) -> bool:
        """SKU 是否存在（不抛错）。"""
        self._validate_sku(sku)
        with self._lock:
            return sku in self._skus

    def _require_sku(self, sku: str) -> _SkuState:
        # 仅在持有 self._lock 时调用
        try:
            return self._skus[sku]
        except KeyError:
            raise SKUNotFoundError(f"SKU {sku!r} 不存在") from None

```
