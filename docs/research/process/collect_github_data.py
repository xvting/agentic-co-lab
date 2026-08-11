# -*- coding: utf-8 -*-
"""TK-013 GitHub 热门 AI Agent 项目调研 —— 数据采集脚本（过程留痕）
数据源: GitHub REST API (https://api.github.com)
- /repos/{owner}/{repo}       每个候选项目的完整元数据
- /search/repositories        按 topic/关键词的 Top 排序检索
输出: docs/research/data/raw/*.json, data/search/*.json, data/ledger.csv
"""
import json, time, csv, os, urllib.request, urllib.parse, datetime

BASE = "https://api.github.com"
HEADERS = {"User-Agent": "TK-013-research/agentic-colab", "Accept": "application/vnd.github+json"}
SNAPSHOT_UTC = datetime.datetime.now(datetime.timezone.utc).isoformat(timespec="seconds")

OUT_DIR = r"E:\RESEARCH\agentic\docs\research\data"
RAW_DIR = os.path.join(OUT_DIR, "raw")
SEARCH_DIR = os.path.join(OUT_DIR, "search")
os.makedirs(RAW_DIR, exist_ok=True)
os.makedirs(SEARCH_DIR, exist_ok=True)

def api(path):
    url = BASE + path
    req = urllib.request.Request(url, headers=HEADERS)
    with urllib.request.urlopen(req, timeout=30) as resp:
        return json.loads(resp.read().decode("utf-8"))

# ---------- 候选项目清单（按生态角色分组，owner/name） ----------
REPOS = {
  "框架与SDK": [
    "langchain-ai/langgraph", "langchain-ai/langchain", "openai/openai-agents-python",
    "openai/openai-agents-node", "anthropics/claude-agent-sdk", "huggingface/smolagents",
    "pydantic/pydantic-ai", "google/adk-python", "microsoft/semantic-kernel",
    "run-llama/llama_index", "mastra-ai/mastra", "vercel/ai", "microsoft/agent-framework",
  ],
  "多智能体编排": [
    "microsoft/autogen", "ag2ai/ag2", "crewAIInc/crewAI", "geekan/MetaGPT",
    "camel-ai/camel", "modelscope/agentscope", "openai/swarm", "awslabs/multi-agent-orchestrator",
  ],
  "Agent应用/编码智能体": [
    "All-Hands-AI/OpenHands", "Significant-Gravitas/AutoGPT", "cline/cline",
    "Aider-AI/aider", "continuedev/continue", "opencode-ai/opencode",
    "elizaOS/eliza", "openai/codex", "Skyvern-AI/skyvern", "browser-use/browser-use",
  ],
  "平台/低代码": [
    "langgenius/dify", "langflow-ai/langflow", "n8n-io/n8n",
    "FlowiseAI/Flowise", "open-webui/open-webui", "lobehub/lobe-chat",
  ],
  "协议/基础设施/记忆": [
    "modelcontextprotocol/modelcontextprotocol", "modelcontextprotocol/servers",
    "agent-network-protocol/agent-network-protocol", "mem0ai/mem0", "letta-ai/letta",
  ],
}

# ---------- 检索查询（客观性：按 star 排序的 topic/关键词结果） ----------
SEARCHES = {
  "topic-ai-agents": "topic:ai-agents",
  "topic-agent-framework": "topic:agent-framework",
  "topic-multi-agent": "topic:multi-agent",
  "topic-mcp": "topic:mcp",
  "keyword-ai-agent": "ai agent",
}

errors = []
records = []

for group, repos in REPOS.items():
    for full in repos:
        try:
            d = api(f"/repos/{full}")
            d["_snapshot_utc"] = SNAPSHOT_UTC
            d["_group"] = group
            fn = full.replace("/", "__") + ".json"
            with open(os.path.join(RAW_DIR, fn), "w", encoding="utf-8") as f:
                json.dump(d, f, ensure_ascii=False, indent=2)
            records.append({
                "group": group, "full_name": full,
                "stars": d.get("stargazers_count"), "forks": d.get("forks_count"),
                "open_issues": d.get("open_issues_count"), "watchers": d.get("subscribers_count"),
                "license": (d.get("license") or {}).get("spdx_id") if d.get("license") else None,
                "created_at": d.get("created_at"), "pushed_at": d.get("pushed_at"),
                "updated_at": d.get("updated_at"), "archived": d.get("archived"),
                "language": d.get("language"), "topics": ",".join(d.get("topics") or []),
                "html_url": d.get("html_url"), "description": (d.get("description") or "")[:200],
            })
            print(f"OK  {full}  stars={d.get('stargazers_count')}")
        except Exception as e:
            errors.append((full, str(e)))
            print(f"ERR {full}  {e}")
        time.sleep(0.35)

for key, q in SEARCHES.items():
    try:
        url = "/search/repositories?q=" + urllib.parse.quote(q) + "&sort=stars&order=desc&per_page=30"
        s = api(url)
        s["_snapshot_utc"] = SNAPSHOT_UTC
        s["_query"] = q
        with open(os.path.join(SEARCH_DIR, key + ".json"), "w", encoding="utf-8") as f:
            json.dump(s, f, ensure_ascii=False, indent=2)
        print(f"SEARCH OK {key}: total={s.get('total_count')}")
    except Exception as e:
        errors.append(("search:" + key, str(e)))
        print(f"SEARCH ERR {key}: {e}")
    time.sleep(7)  # 未认证搜索接口限 10 次/分钟

# ---------- 台账 CSV ----------
with open(os.path.join(OUT_DIR, "ledger.csv"), "w", newline="", encoding="utf-8-sig") as f:
    w = csv.DictWriter(f, fieldnames=list(records[0].keys()))
    w.writeheader()
    w.writerows(records)

meta = {"snapshot_utc": SNAPSHOT_UTC, "repo_count": len(records), "search_count": len(SEARCHES), "errors": errors}
with open(os.path.join(OUT_DIR, "collection_meta.json"), "w", encoding="utf-8") as f:
    json.dump(meta, f, ensure_ascii=False, indent=2)

print("\nDONE. records=", len(records), "errors=", errors)
print("snapshot_utc=", SNAPSHOT_UTC)
