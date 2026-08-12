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