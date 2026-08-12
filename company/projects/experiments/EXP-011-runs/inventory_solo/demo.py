# -*- coding: utf-8 -*-
"""演示 inventory 模块在验收场景 S1~S7 下的用法。

运行: python demo.py
全部通过时退出码为 0，否则为 1。
"""

import sys
import threading

from inventory import (
    Inventory,
    InventoryError,
    InsufficientStockError,
    InvalidQuantityError,
    ReservationExceededError,
    SkuNotFoundError,
)

_FAILED = []


def check(label: str, cond: bool) -> None:
    print(f"  [{'PASS' if cond else 'FAIL'}] {label}")
    if not cond:
        _FAILED.append(label)


def expect(label: str, exc_type: type, fn) -> None:
    """断言 fn() 抛出 exc_type 类型异常。"""
    try:
        fn()
    except exc_type:
        print(f"  [PASS] {label}")
        return
    except Exception as exc:  # noqa: BLE001 - 演示脚本需捕获全部错误类型
        print(f"  [FAIL] {label}：抛出其他异常 {type(exc).__name__}: {exc}")
        _FAILED.append(label)
        return
    print(f"  [FAIL] {label}：未抛出 {exc_type.__name__}")
    _FAILED.append(label)


def concurrent(n_threads: int, fn, arg_fn):
    """启动 n_threads 个线程并同时触发，返回 [(是否成功, 异常类型)]。"""
    barrier = threading.Barrier(n_threads)
    results = [None] * n_threads

    def worker(i: int) -> None:
        barrier.wait()
        try:
            fn(arg_fn(i))
            results[i] = (True, None)
        except Exception as exc:  # noqa: BLE001
            results[i] = (False, type(exc))

    threads = [threading.Thread(target=worker, args=(i,)) for i in range(n_threads)]
    for t in threads:
        t.start()
    for t in threads:
        t.join()
    return results


def main() -> int:
    print("== S1 入库 ==")
    inv = Inventory()
    inv.register_sku("SKU-A")
    inv.receive("SKU-A", 100)
    check("入库 100 后总库存 == 100", inv.total_stock("SKU-A") == 100)
    check("入库 100 后可用库存 == 100", inv.available_stock("SKU-A") == 100)

    print("== S2 出库与不足 ==")
    inv.ship("SKU-A", 30)
    check("出库 30 后总库存 == 70", inv.total_stock("SKU-A") == 70)
    check("出库 30 后可用库存 == 70", inv.available_stock("SKU-A") == 70)
    expect("再出库 80 抛 InsufficientStockError", InsufficientStockError,
           lambda: inv.ship("SKU-A", 80))
    check("出库失败后库存仍为 70",
          inv.total_stock("SKU-A") == 70 and inv.available_stock("SKU-A") == 70)

    print("== S3 预留与防超卖 ==")
    inv.reserve("SKU-A", 50)
    check("预留 50 后可用库存 == 20", inv.available_stock("SKU-A") == 20)
    expect("再预留 30 抛 ReservationExceededError", ReservationExceededError,
           lambda: inv.reserve("SKU-A", 30))
    check("预留失败后可用仍为 20", inv.available_stock("SKU-A") == 20)
    expect("预留后出库 30 抛 InsufficientStockError", InsufficientStockError,
           lambda: inv.ship("SKU-A", 30))
    check("出库失败后可用仍为 20", inv.available_stock("SKU-A") == 20)
    check("全程未出现负库存",
          inv.total_stock("SKU-A") == 70 and inv.available_stock("SKU-A") == 20)

    print("== S4 释放 ==")
    inv.release("SKU-A", 50)
    check("释放 50 后可用库存 == 70", inv.available_stock("SKU-A") == 70)

    print("== S5 阈值告警 ==")
    inv.set_threshold("SKU-A", 80)
    check("阈值 80 时低库存列表含 SKU-A", inv.low_stock_skus() == ["SKU-A"])
    inv.set_threshold("SKU-A", 60)
    check("阈值 60 时低库存列表不含 SKU-A", inv.low_stock_skus() == [])

    print("== S6 并发安全 ==")
    # 8 线程各入库 10 件
    c = Inventory()
    c.register_sku("SKU-B")
    results = concurrent(8, lambda q: c.receive("SKU-B", q), lambda i: 10)
    check("8 线程入库全部成功", all(ok for ok, _ in results))
    check("8 线程各入库 10 后总库存精确 == 80", c.total_stock("SKU-B") == 80)

    # 100 件库存下 10 线程各出库 30
    c = Inventory()
    c.register_sku("SKU-C")
    c.receive("SKU-C", 100)
    results = concurrent(10, lambda q: c.ship("SKU-C", q), lambda i: 30)
    ok_count = sum(1 for ok, _ in results if ok)
    check("10 线程各出库 30 恰好成功 3 次", ok_count == 3)
    check("出库并发后无负库存",
          c.total_stock("SKU-C") == 10 and c.available_stock("SKU-C") == 10)

    # 100 件库存下 10 线程各预留 30
    c = Inventory()
    c.register_sku("SKU-D")
    c.receive("SKU-D", 100)
    results = concurrent(10, lambda q: c.reserve("SKU-D", q), lambda i: 30)
    ok_count = sum(1 for ok, _ in results if ok)
    check("10 线程各预留 30 恰好成功 3 次", ok_count == 3)
    check("预留并发后可用不为负", c.available_stock("SKU-D") == 10)

    print("== S7 可区分错误 ==")
    expect("查询未注册 SKU 抛 SkuNotFoundError", SkuNotFoundError,
           lambda: inv.total_stock("SKU-NOPE"))
    expect("操作未注册 SKU 抛 SkuNotFoundError", SkuNotFoundError,
           lambda: inv.ship("SKU-NOPE", 1))
    expect("数量为 0 抛 InvalidQuantityError", InvalidQuantityError,
           lambda: inv.receive("SKU-A", 0))
    expect("数量非整数抛 InvalidQuantityError", InvalidQuantityError,
           lambda: inv.receive("SKU-A", 1.5))

    errs = {}
    for name, exc_type, call in [
        ("SkuNotFoundError", SkuNotFoundError, lambda: inv.ship("SKU-NOPE", 1)),
        ("InsufficientStockError", InsufficientStockError, lambda: inv.ship("SKU-A", 10 ** 9)),
        ("InvalidQuantityError", InvalidQuantityError, lambda: inv.ship("SKU-A", -1)),
    ]:
        try:
            call()
        except InventoryError as exc:
            errs[name] = type(exc)
    check("三种错误类型互不相同",
          set(errs) == {"SkuNotFoundError", "InsufficientStockError", "InvalidQuantityError"}
          and len(set(errs.values())) == 3)
    check("全部错误均为 InventoryError 子类",
          all(issubclass(t, InventoryError) for t in errs.values()))

    print()
    if _FAILED:
        print(f"结果：{len(_FAILED)} 项失败 -> {_FAILED}")
        return 1
    print("结果：S1~S7 全部通过（退出码 0）")
    return 0


if __name__ == "__main__":
    sys.exit(main())