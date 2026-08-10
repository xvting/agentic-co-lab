# Operations Manual v0.2

> Distilled from five rounds of experiments (EXP-001~005). Changes: v0.1 → v0.2.

## R1 · Task routing by complexity
| Task characteristics | Mode | Roles |
|---|---|---|
| Low complexity / deterministic | Solo | 1 |
| Medium complexity | Solo by default; collaborate only for high value | 3 |
| High complexity / open / cross-disciplinary | Multi-role collaboration | 3 (sweet spot) |

## R1a · Handling multiple drafts
- Default: **independent generation → select best** (best cost-effectiveness).
- **Merge** only when combining substantive elements (e.g., company-wide OKR).
- More roles add coverage, not quality.

## R2 · Experiment first
- Validate major decisions on a small sample before scaling; never build unneeded infrastructure.
- Every experiment must persist protocol + report, reproducible and traceable.

## R3 · Honest reporting
- Label evidence strength (n, task type, evaluation method).
- "No significant difference" is a valid conclusion.

## R4 · Independent review
- Formal outputs (positioning / vision / OKR / code release) require independent review.
- Declare the relationship between reviewer and author; self-review inflates.

## R5 · Knowledge persistence
- Every decision lands in a formal document, traceable to its evidence.
- Recommended layout:
```
org/
├── charter.md            # charter
├── statements/           # positioning / vision
├── okr.md                # objectives
├── operations-manual.md  # this manual
├── agents/               # role cards
├── meetings/             # meeting notes
└── projects/experiments/ # evidence chain
```

*v0.2 · 2026-08-10 · Evidence: EXP-001~005*
