# The "Agent Startup" Experiment: From Empty Directory to Open-Source Company (One-Day Record)

> Agentic Co-Lab case study · 2026-08-10
> Keywords: multi-agent organization / collaboration experiments / evidence-driven / open-source starter kit

## TL;DR
Built a "virtual company" out of AI agents. Starting from an empty directory, we went through **organization setup → six controlled experiments → methodology → productization → open-source release**, reaching 0→1 and publishing to GitHub in a single day. The core output is not code but an **experimentally validated methodology for multi-agent collaboration** (the Starter Kit).

## 1. Origin
The founder asked an open question: "Can you form an organization to solve problems and achieve goals?"
We concretized it: let a group of AI agents run like a real company — with a charter, roles, meetings, experiments, and products. No paper design; we **actually ran it**.

## 2. How we did it
1. **Scaffold**: charter (mission/vision/values/decision mechanism) + org chart + role cards (identity/training/duties/principles).
2. **First meeting**: 3 "employees" (Researcher/CTO/PM) each proposed a direction → cross-review → vote → merged project.
3. **Experiment first**: no infrastructure before evidence; minimal controlled experiments drove decisions.
4. **Knowledge is the product**: solidified validated methodology into a template pack, open-sourced it.

## 3. Key data (six experiments)
| Exp | Question | Finding | Evidence strength |
|---|---|---|---|
| EXP-001 | Open task: collab vs solo | Collab +19% | n=1, exploratory |
| EXP-002 | Deterministic task: collab vs solo | Collab +0% | 15-case objective suite |
| EXP-003 | Medium complexity | Collab +7% | 13 asserts + subjective |
| EXP-004 | Select-best vs merge | Select-best best ROI | n=1, self-review bias declared |
| EXP-005 | Team size 3/5/7 | Saturates at 3 roles | nested design, n=1 |
| EXP-006 | Starter Kit field test | Full workflow works; R4 works | independent review caught real issues |

**Three core rules**
1. Collaboration value ∝ task openness × complexity (low 0% / mid +7% / high +19%)
2. Select-best quality saturates at 3 roles — more roles add coverage, not quality
3. Default to select-best; merge only to combine substantive elements

## 4. Key decisions & turns
| Decision | Why | Result |
|---|---|---|
| Experiment before infrastructure | Avoid wasted investment | Saved dev cost, got evidence fast |
| The company is the sample | No external resources needed | Zero-friction, same-day experiments |
| Select-best > merge | Merge can drag down the best draft | Better ROI, written into the manual |
| Independent review for formal outputs | Self-review inflates | R4 caught contradictions & missing evidence |
| Persist knowledge as assets | One experiment, many reuses | Starter Kit + case study |

## 5. Pitfalls (honest list)
1. **Self-review inflation**: EXP-004 merge self-scored 23 — author bias; corrected by independent review.
2. **Blind collaboration**: EXP-002 showed deterministic tasks are 4× cost for 0% gain — nearly collaborated for its own sake.
3. **Numbers without context**: early claims lacked baselines/sample sizes; only credible after the review forced completion.
4. **Concurrency limits**: EXP-005's 7th agent briefly failed on the thread cap; needed batching.
5. **Identity mismatch**: global git identity was a Gitee address vs GitHub publishing goal; needed repo-level identity override.

## 6. Takeaways (transferable)
1. **Organization beats models**: roles, processes, and review mechanisms drive output quality more than raw model capability.
2. **Experiments beat arguments**: "Is collaboration useful?" — run a 30-minute controlled test rather than debate.
3. **3 roles is enough to start**: don't start with 7; validate before adding people.
4. **Select-best, don't merge**: pick the best draft in most cases instead of force-merging.
5. **Evidence must be verifiable**: every claim should trace back to experiment records.

## 7. Limitations & outlook
- All experiments have small n (1~3), single reviewer, exploratory — not statistically significant.
- Single-day scope; limited task types (writing/coding/strategy).
- Outlook: external trial feedback → templates v1.2; larger samples; multi-language docs; real business validation.

---
*Full evidence chain: `company/projects/experiments/`; product: `starter-kit/`; org archive: `company/`.*
