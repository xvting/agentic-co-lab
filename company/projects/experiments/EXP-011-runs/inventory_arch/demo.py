"""演示 inventory 模块的 S1~S7 全部验收场景。

运行: python demo.py   （全部通过时退出码为 0）
"""

import threading

from inventory import (
    InsufficientStockError,
    InvalidQuantityError,
    Inventory,
    ReservationError,
    SKUNotFoundError,
)


def _run_concurrently(n, fn):
    """启动 n 个线程同时执行 fn(i)，返回 (成功返回值列表, 异常列表)。"""
    barrier = threading.Barrier(n)
    results, errors = [], []

    def worker(i):
        barrier.wait()
        try:
            results.append(fn(i))
        except Exception as exc:  # 收集预期中的失败
            errors.append(exc)

    threads = [threading.Thread(target=worker, args=(i,)) for i in range(n)]
    for t in threads:
        t.start()
    for t in threads:
        t.join()
    return results, errors


def main() -> int:
    ok = True

    def check(name, cond, detail=""):
        nonlocal ok
        ok = ok and cond
        print(f"[{'PASS' if cond else 'FAIL'}] {name}" + (f"  {detail}" if detail else ""))

    inv = Inventory()

    # ---- S1 入库 ----
    inv.add_stock("SKU-A", 100)
    s = inv.get_stock("SKU-A")
    check("S1 入库100 -> 总/可用=100", s.total == 100 and s.available == 100,
          f"(total={s.total}, available={s.available})")

    # ---- S2 出库与不足 ----
    inv.withdraw("SKU-A", 30)
    s = inv.get_stock("SKU-A")
    check("S2 出库30 -> 总/可用=70", s.total == 70 and s.available == 70,
          f"(total={s.total}, available={s.available})")
    try:
        inv.withdraw("SKU-A", 80)
        check("S2 超量出库80 应失败", False)
    except InsufficientStockError:
        s = inv.get_stock("SKU-A")
        check("S2 超量出库失败且库存不变", s.total == 70 and s.available == 70,
              f"(total={s.total}, available={s.available})")

    # ---- S3 预留与防超卖 ----
    inv.reserve("SKU-A", 50)
    s = inv.get_stock("SKU-A")
    check("S3 预留50 -> 可用=20", s.available == 20 and s.reserved == 50,
          f"(available={s.available}, reserved={s.reserved})")
    try:
        inv.reserve("SKU-A", 30)
        check("S3 超预留30 应失败", False)
    except InsufficientStockError:
        check("S3 超预留失败 可用仍=20", inv.get_stock("SKU-A").available == 20)
    try:
        inv.withdraw("SKU-A", 30)
        check("S3 预留后出库30 应失败(防超卖)", False)
    except InsufficientStockError:
        s = inv.get_stock("SKU-A")
        check("S3 未超卖/无负库存", s.total == 70 and s.available == 20 and s.reserved == 50,
              str(s))

    # ---- S4 释放 ----
    inv.release("SKU-A", 50)
    s = inv.get_stock("SKU-A")
    check("S4 释放50 -> 可用恢复70", s.available == 70 and s.reserved == 0,
          f"(available={s.available}, reserved={s.reserved})")

    # ---- S5 阈值告警 ----
    inv.set_low_stock_threshold("SKU-A", 80)
    check("S5 阈值80 -> 低库存含 SKU-A", "SKU-A" in inv.get_low_stock_skus(),
          f"low={inv.get_low_stock_skus()}")
    inv.set_low_stock_threshold("SKU-A", 60)
    check("S5 阈值60 -> 低库存不含 SKU-A", "SKU-A" not in inv.get_low_stock_skus(),
          f"low={inv.get_low_stock_skus()}")

    # ---- S6 并发 ----
    # 6a: 8 线程各入库 10 -> 总库存精确 +80
    c1 = Inventory()
    _, errs = _run_concurrently(8, lambda i: c1.add_stock("SKU-C", 10))
    s = c1.get_stock("SKU-C")
    check("S6a 8线程x入库10 -> 总=80 且无异常", len(errs) == 0 and s.total == 80,
          f"(total={s.total}, errs={len(errs)})")

    # 6b: 100 库存, 10 线程各出库 30 -> 恰 3 次成功, 不超卖
    c2 = Inventory()
    c2.add_stock("SKU-D", 100)
    succ, errs = _run_concurrently(10, lambda i: c2.withdraw("SKU-D", 30))
    s = c2.get_stock("SKU-D")
    check("S6b 10线程x出库30 -> 恰3次成功", len(succ) == 3, f"(succ={len(succ)})")
    check("S6b 不超卖 总=10 可用=10", s.total == 10 and s.available == 10, str(s))
    check("S6b 失败均为库存不足", len(errs) == 7 and all(isinstance(e, InsufficientStockError) for e in errs))

    # 6c: 100 库存, 10 线程各预留 30 -> 恰 3 次成功, 可用不为负
    c3 = Inventory()
    c3.add_stock("SKU-E", 100)
    succ, errs = _run_concurrently(10, lambda i: c3.reserve("SKU-E", 30))
    s = c3.get_stock("SKU-E")
    check("S6c 10线程x预留30 -> 恰3次成功", len(succ) == 3, f"(succ={len(succ)})")
    check("S6c 已预留=90 可用=10 不为负", s.reserved == 90 and s.available == 10, str(s))
    check("S6c 失败均为库存不足", len(errs) == 7 and all(isinstance(e, InsufficientStockError) for e in errs))

    # ---- S7 可区分错误 ----
    try:
        inv.get_stock("NO-SUCH-SKU")
        check("S7 查询不存在SKU 应报错", False)
    except SKUNotFoundError:
        check("S7 查询不存在SKU -> SKUNotFoundError", True)
    try:
        inv.withdraw("NO-SUCH-SKU", 1)
        check("S7 出库不存在SKU 应报错", False)
    except SKUNotFoundError:
        check("S7 出库不存在SKU -> SKUNotFoundError", True)
    try:
        inv.add_stock("SKU-A", 0)
        check("S7 入库0 应报错", False)
    except InvalidQuantityError:
        check("S7 参数非法(0) -> InvalidQuantityError", True)
    try:
        inv.add_stock("SKU-A", -5)
        check("S7 入库负数 应报错", False)
    except InvalidQuantityError:
        check("S7 参数非法(-5) -> InvalidQuantityError", True)
    try:
        inv.release("SKU-A", 1)
        check("S7 释放超量 应报错", False)
    except ReservationError:
        check("S7 释放超量 -> ReservationError", True)
    check("S7 四类错误类型互不相同",
          len({SKUNotFoundError, InsufficientStockError, InvalidQuantityError, ReservationError}) == 4)

    print()
    print("RESULT:", "ALL SCENARIOS PASSED" if ok else "SOME CHECKS FAILED")
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
