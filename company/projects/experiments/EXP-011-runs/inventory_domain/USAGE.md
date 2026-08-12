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