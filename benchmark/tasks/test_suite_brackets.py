"""统一测试套件 · EXP-002（括号匹配，15 用例客观评测）

已知基线（EXP-002，n=1 探索性）：单人 15/15 = 协作 15/15（+0%）——
确定性/教科书型编码任务，4 稿（单人 1 + 协作 3）功能完全一致、质量均 5/5/5，
协作零质量增益但成本 4 倍。数据源：company/projects/experiments/EXP-002-报告.md
"""
CASES = [
    ("", True),
    ("()", True),
    ("()[]{}", True),
    ("([{}])", True),
    ("((()))", True),
    ("[](){}", True),
    ("(]", False),
    ("([)]", False),
    ("{", False),
    ("}", False),
    (")", False),
    ("][", False),
    ("{[]}", True),
    ("((", False),
    (")(", False),
]

def run_tests(fn):
    passed = 0
    failed = []
    for i, (inp, expected) in enumerate(CASES):
        try:
            got = fn(inp)
        except Exception as e:
            failed.append((i, inp, expected, f"EXC:{type(e).__name__}:{e}"))
            continue
        if got == expected:
            passed += 1
        else:
            failed.append((i, inp, expected, got))
    return passed, len(CASES), failed

if __name__ == "__main__":
    import sys, importlib.util
    path = sys.argv[1]
    spec = importlib.util.spec_from_file_location("sol", path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    passed, total, failed = run_tests(mod.is_valid_brackets)
    print(f"RESULT {passed}/{total}")
    for f in failed:
        print("FAIL", f)
