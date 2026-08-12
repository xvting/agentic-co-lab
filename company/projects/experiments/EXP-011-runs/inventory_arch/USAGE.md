# 库存管理模块接口说明（技术架构视角）

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
