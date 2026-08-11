# 标准任务 · 日志分析器（编码·数据处理类）

## 任务描述（对所有组完全一致）
> 实现一个日志分析模块 `log_analyzer.py`：解析给定格式的服务日志并实现 5 个接口函数。
> 接口签名必须与下表完全一致；只允许使用 Python 标准库；所有函数必须对空输入稳健（返回 `{}` 或 `[]`，不抛异常）。

### 日志格式（逐行解析）
```
<ts> <LEVEL> svc=<service> ep=<endpoint> status=<code> ms=<duration>
```
- 每行由 6 个空白分隔 token 组成；前两个 token 是时间戳与日志级别（任意字符串，原样保留）。
- 后四个 token 必须**按 `svc= ep= status= ms=` 的顺序**出现，且 `status` / `ms` 为**非负十进制整数**（仅由 0-9 组成，不含负号；负数视为非法行跳过）。
- 不满足以上条件的行视为非法行，`parse_logs` 必须跳过。
- 示例：`2026-08-01T10:00:03.000Z ERROR svc=payments ep=/charge status=500 ms=1500`

### 必须实现的接口
| 函数 | 签名 | 行为 |
|---|---|---|
| parse_logs | `parse_logs(text: str) -> list[dict]` | 逐行解析；每行返回一个 dict：`{ts, level, service, endpoint, status, ms}`（`status`/`ms` 为非负 `int`，其余为 `str`）；非法行跳过 |
| count_by_level | `count_by_level(entries: list[dict]) -> dict[str, int]` | 按 `level` 统计条数 |
| error_rate_by_service | `error_rate_by_service(entries: list[dict]) -> dict[str, float]` | 每服务：错误数 / 请求数；`status >= 500` 计为错误；请求数 = 该服务条目数 |
| avg_ms_by_endpoint | `avg_ms_by_endpoint(entries: list[dict]) -> dict[str, float]` | 每 endpoint 的 `ms` 均值（float） |
| top_slowest | `top_slowest(entries: list[dict], top_n: int) -> list[str]` | 按 endpoint 平均 `ms` **降序**返回 endpoint 名列表，最多 `top_n` 个；平均 `ms` 相同按名称**字典序升序**；`top_n <= 0` 或空输入返回 `[]` |

## 自检样例（与正式套件同源）
```
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
```
期望输出（可自校验）：
- `parse_logs(...)` → 10 条记录，首条为 `{"ts": "2026-08-01T10:00:00.000Z", "level": "INFO", "service": "checkout", "endpoint": "/cart/add", "status": 200, "ms": 12}`
- `count_by_level(...)` → `{"INFO": 5, "WARN": 2, "ERROR": 3}`
- `error_rate_by_service(...)` → `{"checkout": 0.25, "payments": 0.3333, "search": 0.3333}`（404 不计错误）
- `avg_ms_by_endpoint(...)` → `{"/cart/add": 13.0, "/checkout": 492.5, "/charge": 840.0, "/search": 191.67, "/refund": 8.0}`
- `top_slowest(..., 3)` → `["/charge", "/checkout", "/search"]`
> ⚠️ 期望值中的 `0.3333`、`191.67` 为**约数**（四舍五入展示）；正式套件按全精度计算并以 1e-9 容差比较，请勿把取整值硬编码为相等判断（如 `== 0.3333`）。

## 组设计建议
- 单人组：1 个独立代理直出
- 协作组：3 角色分工（接口/解析、聚合计算、边界用例）各写 1 版 → 择优或融合
- 可选：+独立测试代理（R4）专攻边界与 tie-break

## 评测（客观 + 主观补充，见 rubric.md）
- 客观：`python tasks/test_suite_log_analyzer.py <你的解文件.py>` → 输出 `RESULT n/m`（含解析、统计、排序、空输入、非法行、tie-break 用例）
- 主观补充（编码类）：可读性 / 健壮性 / 效率（各 1-5）

## 已知基线（EXP-008 首跑基线，n=3 探索性）
单人（单稿）3 份均 30/30，质量分布 14/14/15（可读/健壮/效率，总分 15）；
择优稿 30/30 + 质量 15/15（CTO 视角直出稿，非融合）——接口明确型编码任务，
客观与质量趋同，协作 +0%。数据源：`company/projects/experiments/EXP-008-基线报告.md`。