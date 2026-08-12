"""EXP-011 客观评测电池 · 自行设计接口编码任务（adapter 驱动，33 断言）

设计背景：
- 本任务接口由执行代理自行定义（无预定义接口）→ 无法像 EXP-002/003/008
  那样用单一固定类名/签名直接测试。
- 评测方式：评测方（督导）按各解 USAGE.md 撰写 adapter，把解 API 归一化为
  本文件定义的 canonical 操作；电池只对 canonical 结果断言。
- adapter 约束：只允许使用解的公开 API（以 USAGE.md 为准），禁止改动解代码、
  禁止访问下划线内部成员。adapter 写不出来或需窥探内部 ⇒ 记为接口可用性缺陷，
  相应断言失败。
- canonical 错误语义用字符串状态表达（"ok"/"insufficient"/"unknown"/"invalid"），
  与解的具体错误机制（异常 vs 返回值）解耦。
- S6 并发断言默认重复 3 轮（--repeat），每轮用独立 SKU 防状态污染。

用法：
    python test_suite_inventory_api.py <adapter_module.py> [--repeat N]
输出：RESULT n/33 + FAIL 明细
"""
import sys
import threading
import importlib.util

CONTRACT = """adapter 模块须实现以下 canonical 函数（每解一个 adapter 文件）：

    add(sku, qty)            -> None；qty<=0 或非正整数必须抛 ValueError
    deduct(sku, qty)         -> "ok" | "insufficient" | "unknown"
    stock(sku)               -> int | None   （None = 未知 SKU）
    available(sku)           -> int | None
    reserve(sku, qty)        -> "ok" | "insufficient" | "unknown"
    release(sku, qty)        -> "ok" | "invalid"(超过已预留) | "unknown"
    set_threshold(sku, qty)  -> "ok" | "unknown"
    low_stock()              -> list[str]（低于阈值的 SKU 列表）

说明：canonical 中 sku 恒为 str；qty 恒为 int。adapter 内异常可抛 ValueError
（参数非法），其余 canonical 状态用返回值表达。
"""


def run_battery(adapter, repeat=3):
    checks = []

    def check(name, fn):
        try:
            ok = bool(fn())
        except Exception as exc:  # noqa: BLE001
            checks.append((name, False, f"EXC {type(exc).__name__}: {exc}"))
            return
        checks.append((name, ok, ""))

    # ---- S1 基本入库 ----
    def _s1():
        adapter.add("SKU-A", 100)
        return adapter.stock("SKU-A") == 100 and adapter.available("SKU-A") == 100
    check("s1_add_100_stock", _s1)

    # ---- R2 参数校验（<=0 报错且可区分）----
    for bad in (0, -1):
        def _bad(bad=bad):
            try:
                adapter.add("SKU-BAD", bad)
                return False
            except ValueError:
                return True
        check(f"s2_invalid_qty_add_{bad}", _bad)

    # ---- S2 出库与不足 ----
    check("s2_deduct_30_ok", lambda: adapter.deduct("SKU-A", 30) == "ok")
    check("s2_stock_70", lambda: adapter.stock("SKU-A") == 70)
    check("s2_available_70", lambda: adapter.available("SKU-A") == 70)
    check("s2_deduct_80_insufficient", lambda: adapter.deduct("SKU-A", 80) == "insufficient")
    check("s2_stock_still_70", lambda: adapter.stock("SKU-A") == 70)

    # ---- S7 可区分错误（未知 SKU）----
    check("s7_deduct_unknown", lambda: adapter.deduct("UNKNOWN-X", 1) == "unknown")
    check("s7_stock_unknown", lambda: adapter.stock("UNKNOWN-X") is None)
    check("s7_available_unknown", lambda: adapter.available("UNKNOWN-X") is None)
    check("s7_reserve_unknown", lambda: adapter.reserve("UNKNOWN-X", 1) == "unknown")
    check("s7_release_unknown", lambda: adapter.release("UNKNOWN-X", 1) == "unknown")
    check("s7_threshold_unknown", lambda: adapter.set_threshold("UNKNOWN-X", 5) == "unknown")

    # ---- S3 预留与防超卖 ----
    check("s3_reserve_50_ok", lambda: adapter.reserve("SKU-A", 50) == "ok")
    check("s3_available_20", lambda: adapter.available("SKU-A") == 20)
    check("s3_stock_still_70", lambda: adapter.stock("SKU-A") == 70)
    check("s3_reserve_30_insufficient", lambda: adapter.reserve("SKU-A", 30) == "insufficient")
    check("s3_available_still_20", lambda: adapter.available("SKU-A") == 20)
    check("s3_deduct_30_insufficient", lambda: adapter.deduct("SKU-A", 30) == "insufficient")
    check("s3_available_after_deduct", lambda: adapter.available("SKU-A") == 20)

    # ---- S4 释放 ----
    check("s4_release_50_ok", lambda: adapter.release("SKU-A", 50) == "ok")
    check("s4_available_70", lambda: adapter.available("SKU-A") == 70)
    check("s4_release_over_invalid", lambda: adapter.release("SKU-A", 999) == "invalid")
    check("s4_available_still_70", lambda: adapter.available("SKU-A") == 70)

    # ---- S5 阈值与低库存 ----
    check("s5_set_threshold_80", lambda: adapter.set_threshold("SKU-A", 80) == "ok")
    check("s5_low_contains", lambda: "SKU-A" in adapter.low_stock())
    check("s5_set_threshold_60", lambda: adapter.set_threshold("SKU-A", 60) == "ok")
    check("s5_low_not_contains", lambda: "SKU-A" not in adapter.low_stock())

    # ---- 多 SKU 独立 ----
    def _multi():
        adapter.add("SKU-B", 5)
        if adapter.stock("SKU-B") != 5:
            return False
        if adapter.deduct("SKU-B", 3) != "ok":
            return False
        return adapter.stock("SKU-B") == 2 and adapter.stock("SKU-A") == 70
    check("s_multi_sku_independent", _multi)

    # ---- S6 并发（每断言重复 repeat 轮，独立 SKU）----
    def _conc_add():
        for rep in range(repeat):
            sku = f"CONC-ADD-{rep}"
            threads = [threading.Thread(target=adapter.add, args=(sku, 10)) for _ in range(8)]
            for t in threads:
                t.start()
            for t in threads:
                t.join()
            if adapter.stock(sku) != 80:
                return False
        return True
    check("s6_conc_add_exact_80", _conc_add)

    def _conc_deduct():
        for rep in range(repeat):
            sku = f"CONC-DED-{rep}"
            adapter.add(sku, 100)
            ok_n = {"n": 0}
            lock = threading.Lock()

            def worker():
                if adapter.deduct(sku, 30) == "ok":
                    with lock:
                        ok_n["n"] += 1

            threads = [threading.Thread(target=worker) for _ in range(10)]
            for t in threads:
                t.start()
            for t in threads:
                t.join()
            stock_after = adapter.stock(sku)
            if ok_n["n"] != 3 or stock_after != 10 or stock_after < 0:
                return False
        return True
    check("s6_conc_deduct_exactly_3", _conc_deduct)

    def _conc_reserve():
        for rep in range(repeat):
            sku = f"CONC-RSV-{rep}"
            adapter.add(sku, 100)
            ok_n = {"n": 0}
            lock = threading.Lock()

            def worker():
                if adapter.reserve(sku, 30) == "ok":
                    with lock:
                        ok_n["n"] += 1

            threads = [threading.Thread(target=worker) for _ in range(10)]
            for t in threads:
                t.start()
            for t in threads:
                t.join()
            avail = adapter.available(sku)
            if ok_n["n"] != 3 or avail != 10 or avail < 0:
                return False
        return True
    check("s6_conc_reserve_exactly_3", _conc_reserve)

    passed = sum(1 for _, ok, _ in checks if ok)
    failed = [(n, r) for n, ok, r in checks if not ok]
    return passed, len(checks), failed


def load_adapter(path):
    spec = importlib.util.spec_from_file_location("adapter", path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


if __name__ == "__main__":
    args = [a for a in sys.argv[1:]]
    repeat = 3
    if "--repeat" in args:
        i = args.index("--repeat")
        repeat = int(args[i + 1])
        del args[i:i + 2]
    if not args:
        print(CONTRACT)
        print("用法: python test_suite_inventory_api.py <adapter.py> [--repeat N]")
        sys.exit(2)
    adapter = load_adapter(args[0])
    passed, total, failed = run_battery(adapter, repeat=repeat)
    print(f"RESULT {passed}/{total}")
    for name, reason in failed:
        print("FAIL", name, reason)
