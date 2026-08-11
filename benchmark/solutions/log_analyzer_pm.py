"""log_analyzer.py — 日志分析模块（EXP-008 标准任务，仅标准库）。

逐行解析形如 ``<ts> <LEVEL> svc=<service> ep=<endpoint> status=<code> ms=<duration>``
的服务日志，并提供 5 个接口函数。所有函数对空输入稳健（返回 {} 或 []）。
"""

from __future__ import annotations


def _parse_line(line: str):
    """解析单行日志；不合法时返回 None。

    规则（与任务文档一致）：
      - 恰好 6 个空白分隔 token；
      - token[0] / token[1] 为任意字符串（原样保留）；
      - token[2..5] 必须按 ``svc= ep= status= ms=`` 顺序出现；
      - status / ms 为仅由 0-9 组成的非负十进制整数（负数、空值视为非法）。
    """
    parts = line.split()
    if len(parts) != 6:
        return None
    ts, level = parts[0], parts[1]
    svc, ep, status, ms = parts[2], parts[3], parts[4], parts[5]
    if not (svc.startswith("svc=") and ep.startswith("ep=")
            and status.startswith("status=") and ms.startswith("ms=")):
        return None
    status_digits = status[len("status="):]
    ms_digits = ms[len("ms="):]
    # isdigit 在 ASCII 范围外可能接受 Unicode 数字（如 '²'），故叠加 isascii 校验。
    if not (status_digits and status_digits.isascii() and status_digits.isdigit()
            and ms_digits and ms_digits.isascii() and ms_digits.isdigit()):
        return None
    return {
        "ts": ts,
        "level": level,
        "service": svc[len("svc="):],
        "endpoint": ep[len("ep="):],
        "status": int(status_digits),
        "ms": int(ms_digits),
    }


def parse_logs(text: str) -> list[dict]:
    """逐行解析日志文本；每行返回一个 dict，非法行跳过；空输入返回 []。"""
    return [entry for line in text.splitlines()
            if (entry := _parse_line(line)) is not None]


def count_by_level(entries: list[dict]) -> dict[str, int]:
    """按 level 统计条数；空输入返回 {}。"""
    counts: dict[str, int] = {}
    for entry in entries:
        level = entry["level"]
        counts[level] = counts.get(level, 0) + 1
    return counts


def error_rate_by_service(entries: list[dict]) -> dict[str, float]:
    """每服务：错误数 / 请求数；status >= 500 计为错误；空输入返回 {}。"""
    total: dict[str, int] = {}
    errors: dict[str, int] = {}
    for entry in entries:
        service = entry["service"]
        total[service] = total.get(service, 0) + 1
        if entry["status"] >= 500:
            errors[service] = errors.get(service, 0) + 1
    return {service: errors.get(service, 0) / total[service]
            for service in total}


def avg_ms_by_endpoint(entries: list[dict]) -> dict[str, float]:
    """每 endpoint 的 ms 均值（float）；空输入返回 {}。"""
    total: dict[str, int] = {}
    count: dict[str, int] = {}
    for entry in entries:
        endpoint = entry["endpoint"]
        total[endpoint] = total.get(endpoint, 0) + entry["ms"]
        count[endpoint] = count.get(endpoint, 0) + 1
    return {endpoint: total[endpoint] / count[endpoint]
            for endpoint in total}


def top_slowest(entries: list[dict], top_n: int) -> list[str]:
    """按 endpoint 平均 ms 降序返回至多 top_n 个 endpoint 名。

    平均 ms 相同按名称字典序升序；top_n <= 0 或空输入返回 []。
    """
    if top_n <= 0 or not entries:
        return []
    averages = avg_ms_by_endpoint(entries)
    ranked = sorted(averages.items(), key=lambda item: (-item[1], item[0]))
    return [endpoint for endpoint, _ in ranked[:top_n]]
