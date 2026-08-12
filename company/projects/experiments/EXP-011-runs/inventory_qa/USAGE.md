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
