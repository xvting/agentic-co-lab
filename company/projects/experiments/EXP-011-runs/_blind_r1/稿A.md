# 稿A · USAGE

# 库存管理模块接口说明（inventory.py）

仅使用 Python 标准库，`import inventory` 即可使用。模块提供线程安全的多 SKU 库存容器。

## 1. 类

- `class Inventory()`：线程安全的库存容器，可被多线程安全并发调用。
- `class StockState`：`get()` 返回的只读快照（frozen dataclass），字段：
  - `sku: str` — SKU
  - `total: int` — 总库存
  - `reserved: int` — 已预留量
  - `available: int` — 可用库存（total − reserved）
  - `threshold: int | None` — 低库存阈值；未设置时为 None
- 错误类：全部继承 `StockError(Exception)`，实例带 `sku` 与 `message` 属性。

## 2. 方法签名

| 方法 | 说明 | 返回 |
| --- | --- | --- |
| `receive(sku, quantity) -> int` | 入库；数量须为正整数；不存在时自动建档 | 新总库存 |
| `issue(sku, quantity) -> int` | 出库；只允许扣减可用库存，不足则失败 | 新总库存 |
| `reserve(sku, quantity) -> int` | 预留可用库存；超过可用则失败（防超卖） | 新已预留量 |
| `release(sku, quantity) -> int` | 释放已预留量；超过已预留则失败 | 新已预留量 |
| `set_threshold(sku, threshold) -> int` | 设置低库存阈值（非负整数） | 阈值 |
| `get_threshold(sku) -> int | None` | 查询阈值；未设置为 None | 阈值 |
| `low_stock() -> list[str]` | 返回总库存低于阈值的 SKU 列表（已设阈值者，按字母序） | 列表 |
| `get(sku) -> StockState` | 查询快照；不存在时抛异常 | 快照 |

## 3. 错误语义（区分方式）

以**异常类本身**或 **`e.code`** 区分，各 `code` 互不相同：

| 异常类 | code | 触发条件 |
| --- | --- | --- |
| `InvalidSkuError` | `INVALID_SKU` | sku 不是非空字符串 |
| `InvalidQuantityError` | `INVALID_QUANTITY` | 数量不是正整数（0、负数、非整数、布尔值） |
| `InvalidThresholdError` | `INVALID_THRESHOLD` | 阈值不是非负整数 |
| `SkuNotFoundError` | `SKU_NOT_FOUND` | SKU 合法但未建档（查询或操作时） |
| `InsufficientStockError` | `INSUFFICIENT_STOCK` | 出库量超过可用库存 |
| `ReservationExceededError` | `RESERVATION_EXCEEDED` | 预留量超过可用库存 |
| `ReleaseExceededError` | `RELEASE_EXCEEDED` | 释放量超过已预留量 |

「SKU 不存在」「库存不足」「参数非法」因此天然可区分。

## 4. 最小示例

```python
from inventory import Inventory

inv = Inventory()
inv.receive("SKU-A", 100)          # 总库存/可用库存 = 100
inv.reserve("SKU-A", 50)           # 可用库存 = 50
print(inv.get("SKU-A").available)  # 50
```

## 5. 关键设计决策

数据模型按 SKU 维护总库存、已预留量与阈值；锁策略采用实例级 `RLock`，每次读改写原子完成，杜绝丢更新与超卖。出库与预留都只允许消耗「可用库存（总库存 − 已预留）」，保证任意时刻可用量不为负。错误统一以异常表达，并用独立异常类与 `code` 双通道区分，便于调用方适配与排查。


# 稿A · 模块源码

```python
"""库存管理模块。

为小型电商仓库场景提供线程安全的多 SKU 库存管理：
- SKU 维度管理总库存、已预留量、低库存阈值；
- 支持入库 / 出库 / 预留 / 释放 / 阈值告警 / 查询；
- 全部业务错误通过独立异常类 + code 属性区分；
- 仅使用 Python 标准库。
"""

from __future__ import annotations

import threading
from dataclasses import dataclass
from typing import Dict, List, Optional


class StockError(Exception):
    """库存领域错误基类，所有业务错误均继承本类。"""

    code = "STOCK_ERROR"

    def __init__(self, sku: str, message: str) -> None:
        super().__init__(message)
        self.sku = sku
        self.message = message


class InvalidSkuError(StockError):
    """SKU 参数非法：不是字符串或为空字符串。"""

    code = "INVALID_SKU"


class InvalidQuantityError(StockError):
    """数量参数非法：不是正整数（0、负数、非整数、布尔值）。"""

    code = "INVALID_QUANTITY"


class InvalidThresholdError(StockError):
    """阈值参数非法：不是非负整数。"""

    code = "INVALID_THRESHOLD"


class SkuNotFoundError(StockError):
    """SKU 格式合法但未建档（不存在）。"""

    code = "SKU_NOT_FOUND"


class InsufficientStockError(StockError):
    """出库量超过可用库存（总库存 - 已预留）。"""

    code = "INSUFFICIENT_STOCK"


class ReservationExceededError(StockError):
    """预留量超过可用库存（防超卖）。"""

    code = "RESERVATION_EXCEEDED"


class ReleaseExceededError(StockError):
    """释放量超过已预留量。"""

    code = "RELEASE_EXCEEDED"


@dataclass(frozen=True)
class StockState:
    """get() 返回的只读库存快照。"""

    sku: str
    total: int
    reserved: int
    available: int
    threshold: Optional[int]


class Inventory:
    """线程安全的多 SKU 库存容器。"""

    def __init__(self) -> None:
        self._lock = threading.RLock()
        self._total: Dict[str, int] = {}
        self._reserved: Dict[str, int] = {}
        self._threshold: Dict[str, int] = {}

    # ---- 内部参数校验 ----
    @staticmethod
    def _check_sku(sku: str) -> None:
        if not isinstance(sku, str) or sku == "":
            raise InvalidSkuError(sku, f"SKU 必须为非空字符串，收到: {sku!r}")

    @staticmethod
    def _check_quantity(sku: str, quantity: int) -> None:
        if isinstance(quantity, bool) or not isinstance(quantity, int) or quantity <= 0:
            raise InvalidQuantityError(sku, f"数量必须为正整数，收到: {quantity!r}")

    # ---- 入库 / 出库 ----
    def receive(self, sku: str, quantity: int) -> int:
        """入库：增加总库存；SKU 不存在时自动建档。返回新的总库存。"""
        self._check_sku(sku)
        self._check_quantity(sku, quantity)
        with self._lock:
            self._total[sku] = self._total.get(sku, 0) + quantity
            self._reserved.setdefault(sku, 0)
            return self._total[sku]

    def issue(self, sku: str, quantity: int) -> int:
        """出库：扣减总库存，只允许消耗可用库存；不足则失败。返回新的总库存。"""
        self._check_sku(sku)
        self._check_quantity(sku, quantity)
        with self._lock:
            if sku not in self._total:
                raise SkuNotFoundError(sku, f"SKU 不存在: {sku}")
            available = self._total[sku] - self._reserved[sku]
            if quantity > available:
                raise InsufficientStockError(
                    sku, f"库存不足: 需要 {quantity}, 可用 {available}"
                )
            self._total[sku] -= quantity
            return self._total[sku]

    # ---- 预留 / 释放 ----
    def reserve(self, sku: str, quantity: int) -> int:
        """预留：预占可用库存，超过可用则失败（防超卖）。返回新的已预留量。"""
        self._check_sku(sku)
        self._check_quantity(sku, quantity)
        with self._lock:
            if sku not in self._total:
                raise SkuNotFoundError(sku, f"SKU 不存在: {sku}")
            available = self._total[sku] - self._reserved[sku]
            if quantity > available:
                raise ReservationExceededError(
                    sku, f"预留超过可用库存: 需要 {quantity}, 可用 {available}"
                )
            self._reserved[sku] += quantity
            return self._reserved[sku]

    def release(self, sku: str, quantity: int) -> int:
        """释放：归还已预留量，超过已预留则失败。返回新的已预留量。"""
        self._check_sku(sku)
        self._check_quantity(sku, quantity)
        with self._lock:
            if sku not in self._total:
                raise SkuNotFoundError(sku, f"SKU 不存在: {sku}")
            if quantity > self._reserved[sku]:
                raise ReleaseExceededError(
                    sku,
                    f"释放超过已预留: 需要 {quantity}, 已预留 {self._reserved[sku]}",
                )
            self._reserved[sku] -= quantity
            return self._reserved[sku]

    # ---- 阈值与低库存告警 ----
    def set_threshold(self, sku: str, threshold: int) -> int:
        """设置低库存阈值（非负整数）。返回阈值。"""
        self._check_sku(sku)
        if isinstance(threshold, bool) or not isinstance(threshold, int) or threshold < 0:
            raise InvalidThresholdError(sku, f"阈值必须为非负整数，收到: {threshold!r}")
        with self._lock:
            if sku not in self._total:
                raise SkuNotFoundError(sku, f"SKU 不存在: {sku}")
            self._threshold[sku] = threshold
            return threshold

    def get_threshold(self, sku: str) -> Optional[int]:
        """查询阈值；未设置时返回 None。"""
        self._check_sku(sku)
        with self._lock:
            if sku not in self._total:
                raise SkuNotFoundError(sku, f"SKU 不存在: {sku}")
            return self._threshold.get(sku)

    def low_stock(self) -> List[str]:
        """返回总库存低于阈值（仅统计已设置阈值的 SKU）的列表，按字母序。"""
        with self._lock:
            return sorted(
                sku for sku in self._threshold if self._total[sku] < self._threshold[sku]
            )

    # ---- 查询 ----
    def get(self, sku: str) -> StockState:
        """查询库存快照；SKU 不存在时抛 SkuNotFoundError。"""
        self._check_sku(sku)
        with self._lock:
            if sku not in self._total:
                raise SkuNotFoundError(sku, f"SKU 不存在: {sku}")
            reserved = self._reserved[sku]
            return StockState(
                sku=sku,
                total=self._total[sku],
                reserved=reserved,
                available=self._total[sku] - reserved,
                threshold=self._threshold.get(sku),
            )

```
