"""Log analyzer: parse service logs and compute aggregate stats.

Only the Python standard library is used. Every function is safe on empty
input (returns {} or [] instead of raising).
"""


def _is_uint(s: str) -> bool:
    """True iff s is a non-empty string of ASCII decimal digits (0-9)."""
    return bool(s) and all("0" <= ch <= "9" for ch in s)


def parse_logs(text: str) -> list[dict]:
    """Parse each line of ``text`` into a dict with keys
    ts, level, service, endpoint, status, ms.  Invalid lines are skipped.

    A valid line has exactly 6 whitespace-separated tokens:
        <ts> <LEVEL> svc=<service> ep=<endpoint> status=<code> ms=<duration>
    where the last four tokens appear in that order and status/ms are
    non-negative decimal integers.
    """
    entries = []
    for line in text.splitlines():
        tokens = line.split()
        if len(tokens) != 6:
            continue
        ts, level, svc_tok, ep_tok, status_tok, ms_tok = tokens
        if not (svc_tok.startswith("svc=") and ep_tok.startswith("ep=")
                and status_tok.startswith("status=") and ms_tok.startswith("ms=")):
            continue
        status_str = status_tok[len("status="):]
        ms_str = ms_tok[len("ms="):]
        if not (_is_uint(status_str) and _is_uint(ms_str)):
            continue
        entries.append({
            "ts": ts,
            "level": level,
            "service": svc_tok[len("svc="):],
            "endpoint": ep_tok[len("ep="):],
            "status": int(status_str),
            "ms": int(ms_str),
        })
    return entries


def count_by_level(entries: list[dict]) -> dict[str, int]:
    """Count entries grouped by ``level``."""
    counts: dict[str, int] = {}
    for entry in entries:
        level = entry["level"]
        counts[level] = counts.get(level, 0) + 1
    return counts


def error_rate_by_service(entries: list[dict]) -> dict[str, float]:
    """Per-service error rate = errors / requests.

    A request with status >= 500 counts as an error; the request count is
    the number of entries for that service.
    """
    totals: dict[str, int] = {}
    errors: dict[str, int] = {}
    for entry in entries:
        service = entry["service"]
        totals[service] = totals.get(service, 0) + 1
        if entry["status"] >= 500:
            errors[service] = errors.get(service, 0) + 1
    return {svc: errors.get(svc, 0) / totals[svc] for svc in totals}


def avg_ms_by_endpoint(entries: list[dict]) -> dict[str, float]:
    """Mean ``ms`` per endpoint (as a float)."""
    sums: dict[str, int] = {}
    counts: dict[str, int] = {}
    for entry in entries:
        endpoint = entry["endpoint"]
        sums[endpoint] = sums.get(endpoint, 0) + entry["ms"]
        counts[endpoint] = counts.get(endpoint, 0) + 1
    return {ep: sums[ep] / counts[ep] for ep in sums}


def top_slowest(entries: list[dict], top_n: int) -> list[str]:
    """Endpoints ranked by mean ``ms`` descending, at most ``top_n``.

    Equal means are broken by endpoint name in ascending lexicographic
    order.  Returns [] when ``top_n <= 0`` or ``entries`` is empty.
    """
    if top_n <= 0 or not entries:
        return []
    averages = avg_ms_by_endpoint(entries)
    ranked = sorted(averages, key=lambda ep: (-averages[ep], ep))
    return ranked[:top_n]
