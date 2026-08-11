# How to Verify the Value of Multi-Agent Collaboration

> Methodology document · Based on real experimental evidence from Agentic Co-Lab EXP-001–009 (n=1–3, exploratory)
> Version v1.0 · 2026-08-11 · Publicly citable/shareable · English
> Bilingual: this English version ↔ the Chinese original [verification-methodology.md](verification-methodology.md); sections and experiment IDs correspond one-to-one, and all figures are identical in both files.
> Evidence sources: `company/projects/experiments/` (EXP-001–009 reports), `benchmark/README.md`, `company/operations-manual.md` (R2/R3/R4)

## 1. Core idea: answer "does collaboration help?" with controlled experiments

"Does multi-agent collaboration actually work?" cannot be settled by intuition. Reframe it as a **falsifiable controlled question**: on the same standardized task, does the collaborating team significantly outperform a single agent working directly, on objective or blind-reviewed metrics — and is the gain worth the extra cost?

- Independent variable: team design (single agent vs multi-role collaboration)
- Dependent variable: output quality (objective pass rate / blind-reviewed score)
- Cost variable: number of agents × rounds
- Decision rule: quality gain vs cost multiple (in our measurements, gains appeared only on open-ended tasks, and typically came with a 4× cost)

## 2. Five key design elements

1. **Standardized task**: use benchmark tasks with unified task descriptions and evaluation, so results are comparable across experiments and teams.
2. **Control group**: always include a "single-agent direct output" baseline arm. A collaboration-only arm with no baseline is not evidence.
3. **Prefer objective evaluation**: use test suites for coding/data tasks (`RESULT n/m`); use a unified rubric scale for subjective tasks (5 dimensions × 1–5). Be objective whenever you can.
4. **Blind review**: outputs are anonymized with IDs, and reviewers are separated from authors; any self-assessment must be declared (the lesson from EXP-001: the reviewer knew each draft's attribution, which introduced preference bias).
5. **Evidence labeling**: each conclusion records n, task type, evaluation method, and scope (R3 honest reporting); "no significant difference" is a valid conclusion too.

## 3. Standard experimental procedure (8 steps)

1. **Choose a task**: pick a standardized task from `benchmark/tasks/` (currently 6 tasks).
2. **Define the design**: single-agent arm + collaboration arm; 3 roles by default; specify the processing path (independent generation → select-best, or merging).
3. **Write the protocol**: ID / date / task / team design / evaluation method (R2: protocol first, traceable).
4. **Execute**: each agent produces independently, without communicating; archive outputs to disk and anonymize them with IDs.
5. **Evaluate**: objective tasks run the test suite; subjective tasks are blind-reviewed against `tasks/rubric.md` (reviewer ≠ author).
6. **Record cost**: number of agents × rounds, then compute cost-effectiveness (quality score ÷ cost units).
7. **Write the report**: record verbatim outputs, evaluation, cost, conclusions, and limitations per the benchmark report template.
8. **Consolidate**: fold conclusions back into the README baselines; update the operations manual when needed.

## 4. Two real examples (positive vs negative)

**Positive · EXP-001 open-ended copywriting (positioning statement)**
Solo draft: **16/25**; 3-role collaboration → merged draft **19/25 (+19%)**; cost: 1 → 4 cost units. Mechanism: researcher/engineer/product perspectives complemented one another, and the integrated draft was clearly better on clarity and executability. Limitations: n=1, single task, and the blind review was not strict (the reviewer knew each draft's attribution).

**Negative · EXP-002 deterministic coding (bracket-matching algorithm)**
Objective evaluation on 15 test cases: solo **15/15 = collaboration 15/15** (all four drafts full marks; quality 5/5/5), gain **+0%**; cost still 4×. Mechanism: for textbook-level tasks, a single direct pass is already optimal; multi-role collaboration is redundant work.

→ Takeaway: **collaboration value ∝ task openness × complexity**. Collaboration on deterministic tasks is pure waste; on open, multi-dimensional tasks it produces real gains.

## 5. Verified findings vs unverified limitations

**Verified (evidence EXP-001–009, n=1–3, exploratory)**
1. Collaboration on deterministic / interface-specified coding tasks: +0% (EXP-002; EXP-008: 30/30 ×3).
2. On analytical reasoning tasks, a single direct pass already converges on the root-cause analysis; the select-best draft equals the best individual draft, +0% (EXP-009: 23/23/25 → 25/25).
3. Open, multi-dimensional tasks show a collaboration gain (EXP-001: +19%), but the sample is extremely small.
4. Medium-complexity coding shows only a marginal gain, +7% (EXP-003: 14/15 → 15/15), driven by select-best + integration rather than role complementarity.
5. 3 roles is the sweet spot for select-best (EXP-005: saturates at 23/25; 5/7 add nothing); select-best has better ROI than merging (EXP-004, R1a).
6. R4 independent review is currently the most stable positive increment (EXP-006/007: select-best draft 22 → review-revised 24, ≈ +9%, for a cost of only +1 reviewer agent).

**Unverified limitations (honest boundaries)**
- All experiments are n=1–3, single reviewer, exploratory — not statistically significant and not generalizable.
- Blind/self-review bias is not eliminated (EXP-001: known attribution; EXP-007: the adopted draft was self-scored by the CEO).
- Ceiling effects (30/30, 25/25) mask finer-grained differences (EXP-008/009).
- The threshold for collaboration gains is not located: "behaviorally open" tasks such as small API designs have not been tested.
- Single agent stack, single round; conclusions may change after model/protocol updates.

## 6. How to reproduce: run your own controlled experiment with the benchmark suite

1. **Coding tasks (objective)**: `python tasks/test_suite_brackets.py <your solution file>` (ttlcache and log_analyzer suites also available), which outputs `RESULT n/m`.
2. **Copywriting / strategy / analysis tasks (subjective)**: use the task descriptions in `benchmark/tasks/task-*.md` and have the solo and team arms each produce output → blind-review against `tasks/rubric.md` (the authoritative rubric, not the scaffolding template) → record cost.
3. Submit per the report template and compare against the EXP-001–009 baselines in the README.
4. When reproducing, **do not change the task or the rubric** — change only the team design; otherwise the results are not comparable.

## 7. Links to the other mechanisms

- **R4 independent review**: formal outputs (positioning / OKRs) go through independent review; "select-best → review → revise" adds ≈ +9% (EXP-007), and is recommended as a standard step.
- **Role-count sweet spot**: default to 3 roles; more roles add dimension coverage, not quality ceiling (EXP-005).
- **Select-best > merge**: default to independent generation → select-best (best ROI); merging is reserved for combining substantive elements from multiple parties (R1a); self-scored merged drafts carry an inflation risk and must go through independent review (EXP-004).
- **Routing rule (R1)**: deterministic / well-specified tasks → single-agent direct output; open, high-complexity tasks → 3-role collaboration + R4.

---
*All figures trace back to the experiment reports in `company/projects/experiments/` and the empirical baselines in `benchmark/README.md`.*