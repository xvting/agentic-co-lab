# Benchmark · 多智能体协作标准评测套件

> 统一评测口径，让不同团队/实验的产出可对比、可复现。
> 依据 Agentic Co-Lab EXP-001~005 沉淀。配套文档：`starter-kit/playbook/`、`starter-kit/templates/rubric.md`。

## 任务清单（当前 4 个标准任务）
| 任务 | 类型 | 评测方式 | 文件 |
|---|---|---|---|
| 括号匹配 | 编码·确定性 | 客观测试套件 | `tasks/test_suite_brackets.py` |
| TTL 缓存 | 编码·功能+设计 | 客观断言 + 主观 | `tasks/test_suite_ttlcache.py` |
| 定位声明 | 文案·开放 | 主观量表（5 维） | `tasks/task-writing-positioning.md` |
| OKR 制定 | 战略·开放 | 主观量表（5 维） | `tasks/task-strategy-okr.md` |

## 怎么跑
### 编码任务（客观）
```bash
python tasks/test_suite_brackets.py <你的解文件.py>   # 输出 RESULT n/m
python tasks/test_suite_ttlcache.py <你的解文件.py>
```

### 文案/战略任务（主观）
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

## 三条实证基准线（来自 EXP-001~005，供对照）
- 开放文案：单人 16/25，3 角色协作融合 19/25（+19%）
- 确定性编码：单人 15/15 = 协作 15/15（+0%）
- 中等编码：单人 14/25，协作整合 15/25（+7%）
- 角色数：择优上限 3 角色饱和（23/25），5/7 无增量
