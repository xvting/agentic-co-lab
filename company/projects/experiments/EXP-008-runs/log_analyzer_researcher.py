"""日志分析器：解析给定格式的服务日志并实现 5 个接口函数。

日志格式（逐行解析）:
    <ts> <LEVEL> svc=<service> ep=<endpoint> status=<code> ms=<duration>

仅使用 Python 标准库；所有函数对空输入稳健（返回 {} 或 []，不抛异常）。
"""

from collections import defaultdict

_FIELDS = ("svc=", "ep=", "status=", "ms=")


def parse_logs(text: str) -> list[dict]:
    """逐行解析日志文本；非法行跳过，返回 [{ts, level, service, endpoint, status, ms}]。"""
    entries = []
    for line in text.splitlines():
        parts = line.split()
        if len(parts) != 6:
            continue
        ts, level = parts[0], parts[1]
        tokens = parts[2:]
        if any(not tok.startswith(prefix) for tok, prefix in zip(tokens, _FIELDS)):
            continue
        status = tokens[2][len("status="):]
        ms = tokens[3][len("ms="):]
        # status / ms 必须为非负十进制整数（仅 0-9，不含负号）
        if not (status.isdigit() and ms.isdigit()):
            continue
        entries.append({
            "ts": ts,
            "level": level,
            "service": tokens[0][len("svc="):],
            "endpoint": tokens[1][len("ep="):],
            "status": int(status),
            "ms": int(ms),
        })
    return entries


def count_by_level(entries: list[dict]) -> dict[str, int]:
    """按 level 统计条数。"""
    counts: dict[str, int] = {}
    for entry in entries:
        level = entry["level"]
        counts[level] = counts.get(level, 0) + 1
    return counts


def error_rate_by_service(entries: list[dict]) -> dict[str, float]:
    """每服务错误率：错误数 / 请求数；status >= 500 计为错误。"""
    totals: dict[str, int] = defaultdict(int)
    errors: dict[str, int] = defaultdict(int)
    for entry in entries:
        service = entry["service"]
        totals[service] += 1
        if entry["status"] >= 500:
            errors[service] += 1
    return {service: errors[service] / totals[service] for service in totals}


def avg_ms_by_endpoint(entries: list[dict]) -> dict[str, float]:
    """每 endpoint 的 ms 均值（float）。"""
    sums: dict[str, int] = defaultdict(int)
    counts: dict[str, int] = defaultdict(int)
    for entry in entries:
        endpoint = entry["endpoint"]
        sums[endpoint] += entry["ms"]
        counts[endpoint] += 1
    return {endpoint: sums[endpoint] / counts[endpoint] for endpoint in sums}


def top_slowest(entries: list[dict], top_n: int) -> list[str]:
    """按 endpoint 平均 ms 降序返回至多 top_n 个；平均相同按名称字典序升序。"""
    if top_n <= 0:
        return []
    avgs = avg_ms_by_endpoint(entries)
    ordered = sorted(avgs.items(), key=lambda item: (-item[1], item[0]))
    return [endpoint for endpoint, _ in ordered[:top_n]]
