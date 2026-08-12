# EXP-011 执行落档目录

执行代理按方案 `EXP-011-方案.md` 第 6 节要求产出并落盘于此（**由 CEO spawn 独立执行代理**，互不沟通、不读取他人草稿；督导不代产出）：

- `inventory_solo/`（单人组·通用视角）：`inventory.py` + `demo.py` + `USAGE.md`
- `inventory_arch/`（协作组·技术负责人·接口与架构）：同 3 文件
- `inventory_domain/`（协作组·业务领域专家·库存域与调用方视角）：同 3 文件
- `inventory_qa/`（协作组·质量与并发工程师·健壮性与测试）：同 3 文件

约束：严格按任务文档 `benchmark/tasks/task-inventory-api.md`——8 条需求约束、S1~S7 验收场景、只允许标准库、`python demo.py` 退出码 0、USAGE.md 写清错误语义（正文 ≤500 字中文）、无过程解释/自夸。

评测装置（督导使用，**执行代理不得读取**）：
- `_harness/test_suite_inventory_api.py`——adapter 驱动统一断言电池（33 断言，S1~S7 + 并发）
- `_harness/adapter_template.py`——adapter 模板（评测方按各解 USAGE.md 撰写）
- `_harness/reference_impl.py` + `_harness/adapters/_reference_adapter.py`——校准 only（验证套件可运行：33/33；注入错误样例 30/33 确认可检出缺陷），**不计入基线**

盲评：`_blind_r1/` 为匿名副本与映射存档（评分前不查看映射）。
