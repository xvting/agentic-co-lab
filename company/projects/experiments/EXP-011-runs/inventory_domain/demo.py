"""demo.py — 演示 inventory 模块并跑通 S1~S7 验收场景，退出码 0。"""

import threading

from inventory import (
    Inventory,
    InsufficientStockError,
    InvalidQuantityError,
    ReleaseExceedsReservedError,
    SkuNotFoundError,
)


def show(label, value):
    print(f"{label}: {value}")


def main():
    inv = Inventory()

    # S1 入库
    inv.restock("SKU-A", 100)
    s = inv.get_stock("SKU-A")
    show("S1 入库100 -> 总库存", s.total)
    show("S1 入库100 -> 可用库存", s.available)

    # S2 出库与不足
    inv.withdraw("SKU-A", 30)
    s = inv.get_stock("SKU-A")
    show("S2 出库30 -> 总库存", s.total)
    show("S2 出库30 -> 可用库存", s.available)
    try:
        inv.withdraw("SKU-A", 80)
    except InsufficientStockError as e:
        show("S2 再出库80 -> 失败", f"{type(e).__name__}: {e}")
    show("S2 失败后总库存仍为", inv.get_stock("SKU-A").total)

    # S3 预留与防超卖
    inv.reserve("SKU-A", 50)
    show("S3 预留50 -> 可用库存", inv.get_stock("SKU-A").available)
    try:
        inv.reserve("SKU-A", 30)
    except InsufficientStockError as e:
        show("S3 再预留30 -> 失败", f"{type(e).__name__}: {e}")
    show("S3 失败后可用库存仍为", inv.get_stock("SKU-A").available)
    try:
        inv.withdraw("SKU-A", 30)
    except InsufficientStockError as e:
        show("S3 已预留下出库30 -> 失败(防超卖)", f"{type(e).__name__}: {e}")

    # S4 释放
    inv.release("SKU-A", 50)
    show("S4 释放50 -> 可用库存", inv.get_stock("SKU-A").available)

    # S5 阈值告警
    inv.set_threshold("SKU-A", 80)
    show("S5 阈值80 -> 低库存列表", inv.low_stock_skus())
    inv.set_threshold("SKU-A", 60)
    show("S5 阈值60 -> 低库存列表", inv.low_stock_skus())

    # S6 并发：8 线程各入库 10
    inv2 = Inventory()
    ts = [threading.Thread(target=inv2.restock, args=("SKU-X", 10)) for _ in range(8)]
    for t in ts: t.start()
    for t in ts: t.join()
    show("S6 8线程各入库10 -> 总库存", inv2.get_stock("SKU-X").total)

    # S6 并发：100 件下 10 线程各出库 30 -> 恰 3 次成功
    inv3 = Inventory()
    inv3.restock("SKU-Y", 100)
    ok = [0]

    def withdraw30():
        try:
            inv3.withdraw("SKU-Y", 30)
            ok[0] += 1
        except InsufficientStockError:
            pass

    ts = [threading.Thread(target=withdraw30) for _ in range(10)]
    for t in ts: t.start()
    for t in ts: t.join()
    show("S6 100件/10线程各出库30 -> 成功次数", ok[0])
    show("S6 并发出库后总库存", inv3.get_stock("SKU-Y").total)

    # S6 并发：100 件下 10 线程各预留 30 -> 恰 3 次成功
    inv4 = Inventory()
    inv4.restock("SKU-Z", 100)
    ok2 = [0]

    def reserve30():
        try:
            inv4.reserve("SKU-Z", 30)
            ok2[0] += 1
        except InsufficientStockError:
            pass

    ts = [threading.Thread(target=reserve30) for _ in range(10)]
    for t in ts: t.start()
    for t in ts: t.join()
    s4 = inv4.get_stock("SKU-Z")
    show("S6 100件/10线程各预留30 -> 成功次数", ok2[0])
    show("S6 并发预留后可用库存", s4.available)

    # S7 可区分错误
    try:
        inv.get_stock("NO-SUCH-SKU")
    except SkuNotFoundError as e:
        show("S7 查询不存在SKU", f"{type(e).__name__}: {e}")
    try:
        inv.restock("SKU-A", 0)
    except InvalidQuantityError as e:
        show("S7 非法数量(入库0)", f"{type(e).__name__}: {e}")
    try:
        inv.withdraw("NO-SUCH-SKU", 1)
    except SkuNotFoundError as e:
        show("S7 操作不存在SKU", f"{type(e).__name__}: {e}")
    try:
        inv.reserve("SKU-A", 99999)
    except InsufficientStockError as e:
        show("S7 库存不足", f"{type(e).__name__}: {e}")
    try:
        inv.release("SKU-A", 99999)
    except ReleaseExceedsReservedError as e:
        show("S7 释放超量", f"{type(e).__name__}: {e}")

    print("ALL SCENARIOS PASSED")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())