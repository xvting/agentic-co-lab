"""演示库存管理模块（inventory.py）的 S1~S7 全部验收场景。

运行: python demo.py
全部场景通过时打印 PASS 并退出码 0；任一场景失败退出码 1。
"""

import sys
import threading

from inventory import (
    InsufficientStockError,
    InvalidQuantityError,
    Inventory,
    ReservationExceededError,
    SkuNotFoundError,
)


def check(cond: bool, label: str) -> None:
    print(("PASS" if cond else "FAIL"), "-", label)
    if not cond:
        sys.exit(1)


def expect(exc_type, label: str, fn) -> None:
    try:
        fn()
    except exc_type:
        print("PASS -", label)
        return
    except Exception as exc:  # noqa: BLE001 演示脚本需捕获全部异常以报告
        print(f"FAIL - {label} 期望 {exc_type.__name__}, 实际 {type(exc).__name__}: {exc}")
        sys.exit(1)
    print(f"FAIL - {label} 期望 {exc_type.__name__}, 但未抛出异常")
    sys.exit(1)


def run_threads(n: int, target) -> None:
    """用 Barrier 让 n 个线程同时出发，最大化并发竞争。"""
    barrier = threading.Barrier(n)

    def wrapped() -> None:
        barrier.wait()
        target()

    threads = [threading.Thread(target=wrapped) for _ in range(n)]
    for t in threads:
        t.start()
    for t in threads:
        t.join()


def main() -> None:
    inv = Inventory()

    # S1 入库：SKU-A 入库 100 → 总库存 100、可用库存 100
    inv.receive("SKU-A", 100)
    st = inv.get("SKU-A")
    check(st.total == 100 and st.available == 100, "S1 入库 100 → 总库存 100 / 可用 100")

    # S2 出库与不足
    inv.issue("SKU-A", 30)
    st = inv.get("SKU-A")
    check(st.total == 70 and st.available == 70, "S2 出库 30 → 总/可用 70")
    expect(InsufficientStockError, "S2 再出库 80 → 库存不足失败", lambda: inv.issue("SKU-A", 80))
    st = inv.get("SKU-A")
    check(st.total == 70, "S2 失败后库存仍为 70")

    # S3 预留与防超卖
    inv.reserve("SKU-A", 50)
    st = inv.get("SKU-A")
    check(st.available == 20, "S3 预留 50 → 可用 20")
    expect(ReservationExceededError, "S3 再预留 30 → 防超卖失败", lambda: inv.reserve("SKU-A", 30))
    st = inv.get("SKU-A")
    check(st.available == 20, "S3 失败后可用仍为 20")
    expect(InsufficientStockError, "S3 再出库 30 → 失败（不超卖）", lambda: inv.issue("SKU-A", 30))

    # S4 释放
    inv.release("SKU-A", 50)
    st = inv.get("SKU-A")
    check(st.available == 70, "S4 释放 50 → 可用恢复 70")

    # S5 阈值告警
    inv.set_threshold("SKU-A", 80)
    check(inv.low_stock() == ["SKU-A"], "S5 阈值 80 → 低库存列表含 SKU-A")
    inv.set_threshold("SKU-A", 60)
    check(inv.low_stock() == [], "S5 阈值 60 → 低库存列表不再含 SKU-A")

    # S6 并发
    con = Inventory()
    result_lock = threading.Lock()
    success = []

    # 8 线程各入库 10 → 总库存精确 +80
    run_threads(8, lambda: con.receive("SKU-C", 10))
    check(con.get("SKU-C").total == 80, "S6 8 线程各入库 10 → 总库存精确 80")

    # 100 件库存，10 线程各出库 30 → 恰 3 次成功、不超卖
    con.receive("SKU-D", 100)

    def worker_issue() -> None:
        try:
            con.issue("SKU-D", 30)
        except InsufficientStockError:
            return
        with result_lock:
            success.append(1)

    run_threads(10, worker_issue)
    st = con.get("SKU-D")
    check(
        len(success) == 3 and st.total == 10 and st.available == 10,
        "S6 10 线程各出库 30 → 恰 3 次成功、总库存 10、不超卖",
    )

    # 100 件库存，10 线程各预留 30 → 恰 3 次成功、可用不为负
    con.receive("SKU-E", 100)
    success.clear()

    def worker_reserve() -> None:
        try:
            con.reserve("SKU-E", 30)
        except ReservationExceededError:
            return
        with result_lock:
            success.append(1)

    run_threads(10, worker_reserve)
    st = con.get("SKU-E")
    check(
        len(success) == 3 and st.reserved == 90 and st.available == 10,
        "S6 10 线程各预留 30 → 恰 3 次成功、可用 10 不为负",
    )

    # S7 可区分错误
    expect(SkuNotFoundError, "S7 查询不存在 SKU → SKU_NOT_FOUND", lambda: con.get("NO-SKU"))
    expect(SkuNotFoundError, "S7 出库不存在 SKU → SKU_NOT_FOUND", lambda: con.issue("NO-SKU", 1))
    expect(InvalidQuantityError, "S7 入库 0 → INVALID_QUANTITY", lambda: con.receive("SKU-C", 0))
    expect(InvalidQuantityError, "S7 入库 -5 → INVALID_QUANTITY", lambda: con.receive("SKU-C", -5))
    codes = {
        e.code
        for e in (
            SkuNotFoundError("x", ""),
            InsufficientStockError("x", ""),
            InvalidQuantityError("x", ""),
            ReservationExceededError("x", ""),
        )
    }
    check(len(codes) == 4, "S7 不同错误类 code 互不相同")

    print()
    print("全部验收场景（S1~S7）通过。")


if __name__ == "__main__":
    main()
