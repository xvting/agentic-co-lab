# How to Build an Agent Company — Practical Guide v1.1

> Distilled from five real controlled experiments (EXP-001~005) by Agentic Co-Lab.
> Written independently from three perspectives (Researcher / CTO / PM), merged, then revised through independent review (R4).
> Changes v1.0 → v1.1: fixed contradiction in the decision table, added evidence appendix, added role-card template and evaluation SOP.

## 1. Overview
An agent company = a programmable organization of AI agents with distinct professional roles collaborating through defined processes: **standardize "how to cooperate," not just stack models.**

## 2. Getting started (5 steps, with done-criteria)
| # | Step | Done when |
|---|---|---|
| 1 | Define 3 roles (Researcher / CTO / PM), write a role card for each | Each card has identity / expertise / duties / principles / acceptance criteria (template in Appendix B) |
| 2 | Build the minimal loop: task → independent multi-role outputs → unified evaluation → persist conclusion | 1 full loop executed |
| 3 | Write charter & OKR, fixed weekly review; explicit lead agent for dispatch & review | Charter/OKR filed + 1 meeting note |
| 4 | Build test suite & rubric (objective cases + subjective scale + blind review) | Suite runs; rubric anchors defined (SOP in Appendix B) |
| 5 | Run first open, user-facing mini-project | Deliverable + protocol/report archived as a pair |

## 3. Three core methods (evidence-based)
1. **Task routing by complexity**: deterministic/low → solo (collaboration +0%, EXP-002); medium → solo by default, collaborate only for high-value ( +7%, EXP-003); open/high-value → 3-role collaboration (+19%, EXP-001). (Baselines in Appendix A)
2. **3 roles is the sweet spot**: select-best quality saturates at 3 roles; going to 5/7 adds coverage, not quality, at double cost (EXP-005).
3. **Select-best over merge**: after independent generation, pick the best draft — best cost-effectiveness. Merge only when combining substantive elements (e.g., company-wide OKR — an exception where more roles add dimension coverage, not quality; consistent with rule 2). Beware self-review inflation (EXP-004).

## 4. Engineering notes
- **Role card = structured prompt**: identity / expertise / duties / principles; roles converge on deterministic tasks, differ on open tasks.
- **Orchestration**: LangGraph for state & branching, AutoGen for conversational collaboration; go linear → parallel, don't start with complex graphs.
- **Evaluation**: objective tasks via test suite pass-rate; subjective tasks via rubric + anchors + blind review (reviewer separated from author); record cost.
- **Experiment before infrastructure**: validate on a small sample before spending on tooling.

## 5. Common pitfalls (self-check)
1. Collaborating on everything — 4× cost for 0% gain on deterministic tasks.
2. "More roles is better" — 3 is enough for select-best scenarios.
3. Forcing merge of drafts — can drag down the best one; default to select-best.
4. Treating self-review as final — formal outputs need independent review (R4).
5. Numbers without evidence — cite baseline, sample size, and rubric (Appendix A).

## 6. Quick decision table
| Task you face | Action |
|---|---|
| Config tweak / known algorithm | Solo |
| Module / API design | Solo; 3 roles if high-value |
| Strategy / positioning / vision | 3 roles, independent → select-best |
| Company-wide OKR | 3 roles merged; expand to 5-7 for full coverage (exception) |
| Multiple drafts in hand | Select-best first; merge only for substantive complementarity |
| Before shipping anything | Run R4 independent review |

## Appendix A · Evidence table (baseline / sample / rubric)
| Exp | Task type | Solo | Collaboration | Gain | n / rubric |
|---|---|---|---|---|---|
| EXP-001 | Open writing | 16/25 | 19/25 | +19% | n=1; 5-dim CEO blind review |
| EXP-002 | Deterministic coding | 15/15 | 15/15 | 0% | 15-case test suite |
| EXP-003 | Medium coding | 14/25 | 15/25 | +7% | 13 asserts + subjective rubric |
| EXP-004 | Open writing | 21/25 | 23/25 (merge) | +10% | n=1; select-best 22, better ROI |
| EXP-005 | OKR strategy | 23/25 (3-role best) | 5/7 roles +0 | — | nested design, n=1 |

> Limitation: small samples (n=1~3), single reviewer, possible self-review bias; exploratory trends, not statistical significance. Cite this appendix when quoting numbers.

## Appendix B · Role-card template + Evaluation SOP
**Role card template** (copy & fill):
```
# Role Card · {{codename}}
## Identity: codename / department / reports-to
## Training: expertise ×2, focus areas, code of conduct
## Duties: 3 items
## Principles: conclusion-first / suggestions include "what-why-risk-verify" / flag blind spots
```

**Evaluation SOP**:
1. Objective tasks: standalone `test_suite.py` imports the solution, loops cases, prints `RESULT n/m`.
2. Subjective tasks: fixed rubric (clarity / differentiation / executability / appeal / completeness, 1-5) + anchor descriptions.
3. Blind review: anonymize drafts; reviewer separated from author; declare if self-reviewed.
4. Record cost: agents × rounds (tokens when available).
