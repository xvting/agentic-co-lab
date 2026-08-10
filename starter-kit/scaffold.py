#!/usr/bin/env python3
"""Scaffold a minimal agent company in seconds.

Usage:
    python scaffold.py --name "My Agent Co" --mission "..." --dir my-company
    python scaffold.py --name "我的智能体公司" --mission "..." --dir my-company --lang zh

Creates: charter, README, 3 role cards, meeting template, OKR stub.
"""
from __future__ import annotations
import argparse
import pathlib
import sys

EN = {
    "README": "# {name}\n\n> {mission}\n\n## Structure\n- `charter.md` — mission/vision/values\n- `agents/` — 3 role cards (researcher / cto / pm)\n- `meetings/` — meeting notes\n- `okr.md` — objectives\n\n## Getting started\n1. Read each role card, customize expertise & principles.\n2. Set 3 objectives in `okr.md`.\n3. Pick a small open task and run it through 3 roles, then select best.\n",
    "charter": "# Charter · {name}\n\n## Mission\n{mission}\n\n## Vision\n{{describe the future you want to create}}\n\n## Values\n1. Evidence over opinion\n2. Specialization\n3. Open communication\n4. Traceability\n5. Human in command\n\n## Decision mechanism\nProposals from roles -> cross-review -> lead consolidates -> human decides.\n",
    "role": "# Role Card · {role}\n\n## Identity\n- Codename: `{code}`\n- Department: {dept}\n- Reports to: lead\n\n## Expertise (customize)\n- {{expertise 1}}\n- {{expertise 2}}\n- Focus: {{focus areas}}\n- Conduct: conclusions must be evidence-based\n\n## Duties\n- {{duty 1}}\n- {{duty 2}}\n- {{duty 3}}\n\n## Principles\n1. Conclusion first, then evidence.\n2. Every suggestion: what / why / risks / verification.\n3. Proactively flag blind spots in others plans.\n",
    "meeting": "# Meeting Notes\n\n- **Topic**: {{topic}}\n- **Date**: {{YYYY-MM-DD}}\n- **Attendees**: {{roles}}\n\n## Agenda\n1.\n\n## Conclusions\n-\n\n## Action items\n| # | Item | Owner | Due |\n|---|---|---|---|\n| 1 |  |  |  |\n",
    "okr": "# OKR · {name}\n\n> Set 3 objectives, each with 2-3 key results and a measurable target.\n\n## O1 {{objective}}\n- KR1: {{key result with number}}\n\n## O2 {{objective}}\n- KR1: {{key result with number}}\n\n## O3 {{objective}}\n- KR1: {{key result with number}}\n",
    "done": "Created agent company skeleton in {dir}\n\nNext steps:\n1. Customize role cards in agents/\n2. Fill in okr.md objectives\n3. Run your first small open task through the 3 roles\n",
}

ZH = {
    "README": "# {name}\n\n> {mission}\n\n## 结构\n- `charter.md` — 使命/愿景/价值观\n- `agents/` — 3 张角色卡（研究员/CTO/PM）\n- `meetings/` — 会议纪要\n- `okr.md` — 目标\n\n## 上手\n1. 阅读每张角色卡，定制专业背景与原则。\n2. 在 `okr.md` 设置 3 个目标。\n3. 选一个小型开放任务，让 3 角色各自产出，再择优。\n",
    "charter": "# 章程 · {name}\n\n## 使命\n{mission}\n\n## 愿景\n{{描述你想创造的未来}}\n\n## 价值观\n1. 证据先于观点\n2. 专业分工\n3. 开放交流\n4. 可追溯\n5. 人类指挥\n\n## 决策机制\n角色提案 -> 互相评审 -> 主持整合 -> 人类拍板。\n",
    "role": "# 角色卡 · {role}\n\n## 身份\n- 代号：`{code}`\n- 部门：{dept}\n- 汇报对象：主持\n\n## 专业背景（请定制）\n- {{专业领域 1}}\n- {{专业领域 2}}\n- 关注：{{关注方向}}\n- 行为准则：结论必须基于证据\n\n## 职责\n- {{职责 1}}\n- {{职责 2}}\n- {{职责 3}}\n\n## 工作原则\n1. 先结论，后论据。\n2. 每个建议：做什么/为什么/风险/验证。\n3. 主动指出他人方案的盲区。\n",
    "meeting": "# 会议纪要\n\n- **主题**：{{主题}}\n- **日期**：{{YYYY-MM-DD}}\n- **参会者**：{{角色}}\n\n## 议程\n1.\n\n## 结论\n-\n\n## 待办\n| # | 事项 | 负责人 | 截止 |\n|---|---|---|---|\n| 1 |  |  |  |\n",
    "okr": "# OKR · {name}\n\n> 设置 3 个目标，每个目标 2-3 条带量化指标的关键结果。\n\n## O1 {{目标}}\n- KR1: {{带数字的关键结果}}\n\n## O2 {{目标}}\n- KR1: {{带数字的关键结果}}\n\n## O3 {{目标}}\n- KR1: {{带数字的关键结果}}\n",
    "done": "已在 {dir} 生成智能体公司骨架\n\n下一步：\n1. 定制 agents/ 下的角色卡\n2. 填写 okr.md 目标\n3. 选一个小型开放任务，让 3 角色各自产出，再择优\n",
}

ROLES = {
    "researcher": ("researcher", "Research", "研究院/Research"),
    "cto": ("cto", "Engineering", "工程部/Engineering"),
    "pm": ("pm", "Product", "产品部/Product"),
}


def write(path: pathlib.Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")
    print(f"  + {path}")


def main() -> int:
    ap = argparse.ArgumentParser(description="Scaffold a minimal agent company.")
    ap.add_argument("--dir", default="agent-company", help="output directory")
    ap.add_argument("--name", default="My Agent Co", help="company name")
    ap.add_argument("--mission", default="To solve problems with verified, reusable agent organizations.", help="mission statement")
    ap.add_argument("--lang", choices=["en", "zh"], default="en", help="language (default en)")
    args = ap.parse_args()

    lang = ZH if args.lang == "zh" else EN
    out = pathlib.Path(args.dir)
    if out.exists() and any(out.iterdir()):
        print(f"error: {out} already exists and is not empty", file=sys.stderr)
        return 1

    write(out / "README.md", lang["README"].format(name=args.name, mission=args.mission))
    write(out / "charter.md", lang["charter"].format(name=args.name, mission=args.mission))
    for code, dept, zhdept in ROLES.values():
        write(out / "agents" / f"{code}.md", lang["role"].format(role=dept, code=code, dept=zhdept))
    write(out / "meetings" / "_TEMPLATE.md", lang["meeting"])
    write(out / "okr.md", lang["okr"].format(name=args.name))

    print()
    print(lang["done"].format(dir=out))
    return 0


if __name__ == "__main__":
    sys.exit(main())
