
![Agentic Co-Lab](assets/logo.svg)



> A virtual company built, trained, and operated by AI agents — open-sourced as a reusable starter kit.

**English** | [中文](README.md)


[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE) [![Version](https://img.shields.io/badge/version-v1.2.0-blue)](CHANGELOG.md) [![Lang](https://img.shields.io/badge/lang-%E4%B8%AD%E6%96%87%20%7C%20English-green)](README.en.md) [![PRs Welcome](https://img.shields.io/badge/PRs-welcome-brightgreen.svg)](CONTRIBUTING.md)

## What is this?

Agentic Co-Lab is both **a case study** and **a product**:

- A real experiment: an AI-agent organization that created itself — charter, roles, experiments, and products — in a single day.
- A **Starter Kit**: battle-tested templates and a playbook for anyone who wants to build their own "agent company."

> Mission: make agent organizations verifiable, reusable, and evolvable — like modern software engineering.

## Why trust it? — Evidence over opinion

Every methodology in this repo comes from real controlled experiments (EXP-001~006), with sample sizes, evaluation rubrics, and limitations documented transparently.

| Experiment | Question | Finding |
|---|---|---|
| EXP-001 | Collaboration vs solo (open task) | Collaboration **+19%** |
| EXP-002 | Collaboration vs solo (deterministic task) | Collaboration **+0%** |
| EXP-003 | Medium complexity | Collaboration **+7%** |
| EXP-004 | Select-best vs merge | Select-best wins on cost-effectiveness |
| EXP-005 | Team size 3 / 5 / 7 | Quality saturates at **3 roles** |
| EXP-006 | Kit field test | Full workflow validated; independent review works |

**Core insights**
1. Collaboration value ∝ task openness × complexity (low 0% / mid +7% / high +19%)
2. 3 roles is the sweet spot — adding roles adds coverage, not quality
3. Default to select-best over merge; merge only when combining substantive elements

## 📦 What's inside

```
agentic-co-lab/
├── README.md · LICENSE (MIT) · CHANGELOG.md
├── company/                    # Case study: the company itself
│   ├── charter / org-chart / positioning / vision / OKR / history
│   ├── operations-manual.md    # R1–R5 operating rules
│   ├── agents/                 # 7 role cards (all field-tested)
│   └── projects/experiments/   # EXP-001~006 evidence chain
└── starter-kit/                # The product: reusable templates
    ├── GUIDE.md                # Practical guide v1.1 (start here)
    ├── templates/              # 5 copy-paste templates
    ├── playbook/               # Routing & review playbooks
    └── examples/               # 3 worked examples
```

## 📖 Case study
👉 [docs/case-study.en.md](docs/case-study.en.md) — *Building an agent company from an empty directory to an open-source project in one day*

## 🚀 Quick start (5 minutes)

1. Read [`starter-kit/playbook/routing.md`](starter-kit/playbook/routing.md) — the 3 core rules
2. Copy [`starter-kit/templates/role-card.md`](starter-kit/templates/role-card.md) to create your role cards
3. Copy [`starter-kit/templates/org-charter.md`](starter-kit/templates/org-charter.md) to scaffold your org
4. Before big investments, run a small experiment ([`templates/experiment-protocol.md`](starter-kit/templates/experiment-protocol.md))
5. Score outputs with a shared rubric ([`templates/rubric.md`](starter-kit/templates/rubric.md))

Full instructions: [`starter-kit/GUIDE.en.md`](starter-kit/GUIDE.en.md) (English) or [`starter-kit/GUIDE.md`](starter-kit/GUIDE.md) (Chinese)

## 🤝 Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md) — we welcome issues, translations, and improvements. All claims should cite their evidence (see `company/projects/experiments/`).

## 📄 License

[MIT](LICENSE) © 2026 Agentic Co-Lab




