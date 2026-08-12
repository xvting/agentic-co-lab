"""库存管理模块 —— 技术架构视角实现（仅标准库，线程安全）。

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
