"""统一测试套件 · EXP-003（TTLCache，13 断言客观评测）

已知基线（EXP-003，n=1 探索性）：客观 13/13 全过（单人/协作一致）；
主观质量（可读/健壮/效率，总分 15）单人 14/15，协作整合 15/15（+7%），
协作组内方差 10/12/15。数据源：company/projects/experiments/EXP-003-报告.md
"""
import time

def run_tests(CacheCls):
    checks = []
    def check(name, cond):
        checks.append((name, bool(cond)))

    # 1 基本读写
    c = CacheCls(capacity=2)
    c.set("a", 1)
    check("basic_get", c.get("a") == 1)
    # 2 覆盖更新
    c.set("a", 2)
    check("overwrite", c.get("a") == 2)
    # 3 缺失键
    check("missing", c.get("nope") is None)
    # 4 TTL 过期
    c2 = CacheCls(capacity=4)
    c2.set("x", 1, ttl_seconds=0.05)
    time.sleep(0.08)
    check("ttl_expired", c2.get("x") is None)
    # 5 TTL 未过期
    c3 = CacheCls(capacity=4)
    c3.set("y", 2, ttl_seconds=1)
    check("ttl_alive", c3.get("y") == 2)
    # 6 无 TTL 持久
    c4 = CacheCls(capacity=4)
    c4.set("z", 3)
    time.sleep(0.05)
    check("no_ttl_persist", c4.get("z") == 3)
    # 7 LRU 驱逐：访问 a 刷新后，驱逐 b
    c5 = CacheCls(capacity=2)
    c5.set("a", 1); c5.set("b", 2)
    check("lru_pre", c5.get("a") == 1)
    c5.set("c", 3)
    check("lru_evict_b", c5.get("b") is None)
    check("lru_keep_a", c5.get("a") == 1)
    check("lru_keep_c", c5.get("c") == 3)
    # 8 容量=1
    c6 = CacheCls(capacity=1)
    c6.set("a", 1); c6.set("b", 2)
    check("cap1_evict_a", c6.get("a") is None)
    check("cap1_keep_b", c6.get("b") == 2)
    # 9 驱逐后仍可写
    c5.set("d", 4)
    check("write_after_evict", c5.get("d") == 4)

    passed = sum(1 for _, ok in checks if ok)
    failed = [n for n, ok in checks if not ok]
    return passed, len(checks), failed

if __name__ == "__main__":
    import sys, importlib.util
    spec = importlib.util.spec_from_file_location("sol", sys.argv[1])
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    passed, total, failed = run_tests(mod.TTLCache)
    print(f"RESULT {passed}/{total}")
    for f in failed:
        print("FAIL", f)
