# Agentic Company Starter Kit · 智能体公司样板间

> 把"多智能体组织如何协作"的方法论沉淀为可直接复用的模板包。
> 由 Agentic Co-Lab 出品 · 基于 EXP-001~005 五轮真实实验证据。

## 这是什么
一套**开箱即用**的模板与手册，帮你 1 小时内搭建自己的"智能体公司"：
- **角色卡模板** → 为每个智能体注入身份与专业背景
- **组织骨架模板** → 章程、架构、会议规范
- **运营手册** → 任务怎么派、多稿怎么处理、怎么评审（基于实证规律）
- **实验框架** → 用最小成本验证你的协作假设，不拍脑袋
- **示例包** → 直接抄作业的范例

## 为什么可信
所有方法论均来自真实对照实验（n 值、任务类型、评测方式全透明）：

| 实验 | 问题 | 核心结论 |
|---|---|---|
| EXP-001 | 协作 vs 单人（开放任务） | 协作 +19% |
| EXP-002 | 协作 vs 单人（确定性任务） | 协作 +0% |
| EXP-003 | 中等复杂度 | 协作 +7% |
| EXP-004 | 择优 vs 融合 | 择优是性价比甜点 |
| EXP-005 | 角色数 3/5/7 | 3 角色即饱和 |

## 5 分钟上手
1. 读 [`playbook/routing.md`](playbook/routing.md) 了解三条核心规则
2. 复制 [`templates/role-card.md`](templates/role-card.md) 创建你的角色卡
3. 复制 [`templates/org-charter.md`](templates/org-charter.md) 搭公司骨架
4. 接到任务时，按 [`templates/experiment-protocol.md`](templates/experiment-protocol.md) 先小样本验证
5. 用 [`templates/rubric.md`](templates/rubric.md) 统一评分，避免主观扯皮

## 目录结构
```
starter-kit/
├── README.md                # 本文件
├── templates/               # 可复制模板（占位符 {{...}}）
│   ├── role-card.md         # 智能体角色卡
│   ├── org-charter.md       # 公司章程/骨架
│   ├── meeting-notes.md     # 会议纪要
│   ├── experiment-protocol.md  # 实验协议
│   └── rubric.md            # 评测量表
├── playbook/                # 方法论（实证规律）
│   ├── routing.md           # 任务分级路由 + 角色数甜点
│   └── review.md            # 多稿处理 + 独立评审
└── examples/                # 范例（可抄作业）
    ├── role-card-example.md
    ├── vision-example.md
    └── experiment-example.md
```

## 许可证与归属
- 方法论文档：CC-BY（署名即可复用）
- 示例角色卡：Agentic Co-Lab 原创，引用请标注来源

## 📘 实操指南（推荐先读）
👉 [`GUIDE.md`](GUIDE.md) —《智能体公司搭建实操指南 v1.1》
（概述/起步清单/三条核心方法/工程要点/常见坑/自查表/证据附录/角色卡模板与评测 SOP）

## 30 秒起步（脚手架）
一键生成最小智能体公司骨架（章程 + 3 角色卡 + OKR + 会议模板）：

```bash
# English
python scaffold.py --name "My Agent Co" --mission "..." --dir my-company

# 中文
python scaffold.py --name "我的智能体公司" --mission "..." --dir my-company --lang zh
```

## 🧪 完整示例：demo 公司
[`examples/demo-company/`](examples/demo-company/) — 用脚手架生成并跑通首任务的完整示例（骨架 + 定位声明 + 会议纪要 + OKR）。
