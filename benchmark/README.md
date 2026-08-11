# Benchmark · 多智能体协作标准评测套件

> 统一评测口径，让不同团队/实验的产出可对比、可复现。
> 依据 Agentic Co-Lab EXP-001~005 沉淀。配套文档：`starter-kit/playbook/`；评测量表唯一权威来源：`tasks/rubric.md`（`starter-kit/templates/rubric.md` 仅为脚手架模板，不作评测口径）。

## 任务清单（当前 6 个标准任务）
| 任务 | 类型 | 评测方式 | 文件 |
|---|---|---|---|
| 括号匹配 | 编码·确定性 | 客观测试套件 | `tasks/test_suite_brackets.py` |
| TTL 缓存 | 编码·功能+设计 | 客观断言 + 主观 | `tasks/test_suite_ttlcache.py` |
| 定位声明 | 文案·开放 | 主观量表（5 维） | `tasks/task-writing-positioning.md` |
| OKR 制定 | 战略·开放 | 主观量表（5 维） | `tasks/task-strategy-okr.md` |
| 日志分析 | 编码·数据处理 | 客观测试套件 + 主观补充（基线已建立：EXP-008） | `tasks/test_suite_log_analyzer.py` |
| 支付归因 | 分析·推理 | 主观量表（5 维）（基线已建立：EXP-009） | `tasks/task-analysis-attribution.md` |

## 怎么跑
### 编码任务（客观）
```bash
python tasks/test_suite_brackets.py <你的解文件.py>   # 输出 RESULT n/m
python tasks/test_suite_ttlcache.py <你的解文件.py>
python tasks/test_suite_log_analyzer.py <你的解文件.py>
```

### 文案/战略/分析任务（主观）
1. 用 `tasks/task-*.md` 中的任务描述，让单人/协作组各自产出。
2. 用 `tasks/rubric.md`（5 维 × 1-5）盲评。
3. 记录过程成本（代理数 × 轮次）。

## 报告模板（每个实验提交）
```
实验编号 / 日期 / 任务 / 组设计（单人?协作?角色数?）
产出原文（匿名）
评测：客观 n/m + 主观 5 维分
成本：代理数 × 轮次
结论与局限（n、口径、偏差声明）
```

## 实证基准线（EXP-001~009，供对照）
- 开放文案：单人 16/25，3 角色协作融合 19/25（+19%）
- 确定性编码：单人 15/15 = 协作 15/15（+0%）
- 中等编码：单人 14/25，协作整合 15/25（+7%）
- 角色数：择优上限 3 角色饱和（23/25），5/7 无增量
- 支付归因（EXP-009 首跑基线，n=3 探索性）：单人（单稿）质量分布 23/23/25，择优稿 25/25（数据分析师稿）——主观分析任务 3 角色独立直出，分析骨架（根因/对账/可证伪验证）趋同，区分在量化呈现与决策完整度；协作 +0%（择优=最高单稿，详见 EXP-009-基线报告.md）
- 日志分析（EXP-008 首跑基线，n=3 探索性）：单人/多稿均 30/30，择优稿质量 15/15——接口明确型编码任务，客观与质量趋同（协作 +0%），与 EXP-002 一致
