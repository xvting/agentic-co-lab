# Release Announcement (EN) · Agentic Co-Lab v1.2

> English version of the announcement. Authorship: PM (主笔) + Researcher (R4 评审) · Task TK-001 · 2026-08-11

## 🎉 Agentic Co-Lab v1.2 is now open source

A starter kit for standing up your own **agent company** — validated by **7 controlled experiments**, and released under the MIT license.

### This is not another agent framework
Agentic Co-Lab is an **evidence-driven organizational methodology**. It answers the questions most frameworks skip: how to divide work among agents, which tasks actually benefit from collaboration, how many roles are worth hiring, how to pick the best draft, and how to review outputs. Every conclusion is backed by a public experiment record you can inspect and reproduce. Protocols and raw data are fully open, so any team can re-run the entire chain and verify the numbers for themselves.

### Evidence, not opinion
- **7 controlled experiments (EXP-001–007)** — protocols and reports fully public.
- **Three core findings:**
  1. **Collaboration value ∝ task openness × complexity** — 0% for low, +7% for medium, +19% for high openness × complexity.
  2. **Three roles hit the sweet spot** — quality saturates at 3 roles; adding roles adds coverage, not quality.
  3. **Default: pick the best of several drafts** — independent review adds **+9%** quality.
- **One-command scaffold** — bootstrap an agent company with a single command, in English or 中文.

### What's inside
- **Starter Kit** — role cards, org charter, meeting SOP, experiment protocols, and an evaluation rubric, 100% bilingual (EN/中文).
- **GUIDE v1.2** — a practical playbook plus a complete worked example: a demo company run end-to-end.
- **Benchmark** — a standard evaluation suite with four benchmark tasks and a unified scoring rubric, so results are comparable across teams.
- **Case study** — a complete single-day record of building an open-source company from an empty directory.

### Quick start
```bash
git clone https://github.com/xvting/agentic-co-lab
cd agentic-co-lab
python starter-kit/scaffold.py --name "My Agent Co" --dir my-company   # English
python starter-kit/scaffold.py --name "我的智能体公司" --dir my-company --lang zh  # 中文
```

### Get involved
- Want to build an agent company? → Run the scaffold.
- Want to reproduce the results? → Run your own controlled experiments with `benchmark/`.
- Have feedback or ideas? → Issues and PRs are welcome.

**MIT licensed — fork it, use it, ship it.** 🚀
