"""统一测试套件 · EXP-008（日志分析器 Log Analyzer）"""

SAMPLE = """\
2026-08-01T10:00:00.000Z INFO svc=checkout ep=/cart/add status=200 ms=12
2026-08-01T10:00:01.000Z INFO svc=checkout ep=/checkout status=200 ms=85
2026-08-01T10:00:02.000Z WARN svc=payments ep=/charge status=200 ms=180
2026-08-01T10:00:03.000Z ERROR svc=payments ep=/charge status=500 ms=1500
2026-08-01T10:00:04.000Z ERROR svc=checkout ep=/checkout status=502 ms=900
2026-08-01T10:00:05.000Z INFO svc=search ep=/search status=200 ms=45
2026-08-01T10:00:06.000Z ERROR svc=search ep=/search status=500 ms=320
2026-08-01T10:00:07.000Z INFO svc=checkout ep=/cart/add status=200 ms=14
2026-08-01T10:00:08.000Z WARN svc=search ep=/search status=200 ms=210
2026-08-01T10:00:09.000Z INFO svc=payments ep=/refund status=404 ms=8
"""

TIED = """\
2026-08-01T10:00:00.000Z INFO svc=s ep=/b status=200 ms=100
2026-08-01T10:00:01.000Z INFO svc=s ep=/a status=200 ms=100
"""


def close(a, b, tol=1e-9):
    if a is None or b is None:
        return False
    try:
        return abs(a - b) <= tol
    except TypeError:
        return False


def run_tests(mod):
    # 断言分母固定 30：接口缺失时用抛错桩替换，相关断言一律按失败计入
    checks = []
    def check(name, fn):
        try:
            ok = bool(fn())
            reason = ""
        except Exception as e:
            ok = False
            reason = f"{type(e).__name__}: {e}"
        checks.append((name, ok, reason))

    names = ("parse_logs", "count_by_level", "error_rate_by_service",
             "avg_ms_by_endpoint", "top_slowest")
    fns = {}
    for n in names:
        f = getattr(mod, n, None)
        fns[n] = f if callable(f) else None

    def _missing(name):
        def _stub(*args, **kwargs):
            raise AttributeError(f"missing function: {name}")
        return _stub

    for n in names:
        fns[n] = fns[n] if fns[n] is not None else _missing(n)
    parse_logs, count_by_level = fns["parse_logs"], fns["count_by_level"]
    error_rate_by_service = fns["error_rate_by_service"]
    avg_ms_by_endpoint = fns["avg_ms_by_endpoint"]
    top_slowest = fns["top_slowest"]

    reordered = "2026-08-01T10:00:00.000Z INFO status=200 ms=12 svc=checkout ep=/cart/add"
    mixed = "garbage\n" + SAMPLE.splitlines()[0]
    dbg_line = "2026-08-01T10:00:00.000Z DEBUG svc=checkout ep=/ping status=200 ms=0"
    ok_logs = "2026-08-01T10:00:00.000Z INFO svc=x ep=/a status=404 ms=5"

    # ---- parse_logs（8 断言）----
    check("parse_count", lambda: isinstance(parse_logs(SAMPLE), list)
          and len(parse_logs(SAMPLE)) == 10)
    check("parse_fields", lambda: parse_logs(SAMPLE)[3] == {
        "ts": "2026-08-01T10:00:03.000Z", "level": "ERROR",
        "service": "payments", "endpoint": "/charge",
        "status": 500, "ms": 1500,
    })
    check("parse_empty", lambda: parse_logs("") == [])
    check("parse_malformed", lambda: parse_logs("this is not a valid log line") == [])
    check("parse_reordered_skipped", lambda: parse_logs(reordered) == [])
    check("parse_mixed_skip_bad", lambda: len(parse_logs(mixed)) == 1)
    check("parse_unknown_level", lambda: len(parse_logs(dbg_line)) == 1
          and parse_logs(dbg_line)[0]["level"] == "DEBUG")
    check("parse_zero_ms", lambda: len(parse_logs(dbg_line)) == 1
          and parse_logs(dbg_line)[0]["ms"] == 0)

    # ---- count_by_level（3 断言）----
    check("count_levels", lambda: count_by_level(parse_logs(SAMPLE)) == {"INFO": 5, "WARN": 2, "ERROR": 3})
    check("count_levels_empty", lambda: count_by_level([]) == {})
    check("count_levels_unknown", lambda: count_by_level(parse_logs(dbg_line)) == {"DEBUG": 1})

    # ---- error_rate_by_service（6 断言）----
    check("rate_keys", lambda: set(error_rate_by_service(parse_logs(SAMPLE)))
          == {"checkout", "payments", "search"})
    check("rate_checkout", lambda: close(error_rate_by_service(parse_logs(SAMPLE)).get("checkout"), 0.25))
    check("rate_payments", lambda: close(error_rate_by_service(parse_logs(SAMPLE)).get("payments"), 1 / 3))
    check("rate_search", lambda: close(error_rate_by_service(parse_logs(SAMPLE)).get("search"), 1 / 3))
    check("rate_empty", lambda: error_rate_by_service([]) == {})
    check("rate_no_5xx", lambda: close(error_rate_by_service(parse_logs(ok_logs))["x"], 0.0))

    # ---- avg_ms_by_endpoint（7 断言）----
    check("avg_keys", lambda: set(avg_ms_by_endpoint(parse_logs(SAMPLE)))
          == {"/cart/add", "/checkout", "/charge", "/search", "/refund"})
    check("avg_cart_add", lambda: close(avg_ms_by_endpoint(parse_logs(SAMPLE))["/cart/add"], 13.0))
    check("avg_checkout", lambda: close(avg_ms_by_endpoint(parse_logs(SAMPLE))["/checkout"], 492.5))
    check("avg_charge", lambda: close(avg_ms_by_endpoint(parse_logs(SAMPLE))["/charge"], 840.0))
    check("avg_search", lambda: close(avg_ms_by_endpoint(parse_logs(SAMPLE))["/search"], 575 / 3))
    check("avg_refund", lambda: close(avg_ms_by_endpoint(parse_logs(SAMPLE))["/refund"], 8.0))
    check("avg_empty", lambda: avg_ms_by_endpoint([]) == {})

    # ---- top_slowest（6 断言）----
    check("top3", lambda: top_slowest(parse_logs(SAMPLE), 3) == ["/charge", "/checkout", "/search"])
    check("top2", lambda: top_slowest(parse_logs(SAMPLE), 2) == ["/charge", "/checkout"])
    check("top_all", lambda: top_slowest(parse_logs(SAMPLE), 10)
          == ["/charge", "/checkout", "/search", "/cart/add", "/refund"])
    check("top0", lambda: top_slowest(parse_logs(SAMPLE), 0) == [])
    check("top_empty", lambda: top_slowest([], 5) == [])
    check("top_tie", lambda: top_slowest(parse_logs(TIED), 2) == ["/a", "/b"])

    passed = sum(1 for _, ok, _ in checks if ok)
    failed = [(n, r) for n, ok, r in checks if not ok]
    return passed, len(checks), failed


if __name__ == "__main__":
    import sys, importlib.util
    spec = importlib.util.spec_from_file_location("sol", sys.argv[1])
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    passed, total, failed = run_tests(mod)
    print(f"RESULT {passed}/{total}")
    for name, reason in failed:
        print(f"FAIL {name} :: {reason}" if reason else f"FAIL {name}")