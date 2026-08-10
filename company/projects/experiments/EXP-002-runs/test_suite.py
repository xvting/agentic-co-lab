"""统一测试套件 · EXP-002"""
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
