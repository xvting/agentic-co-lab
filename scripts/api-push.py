#!/usr/bin/env python3
"""Push local commits to GitHub via Git Data API (works when git-over-https is blocked)."""
import subprocess, json, base64, sys, re
from datetime import datetime, timezone

REPO = "xvting/agentic-co-lab"

def sh(*args):
    return subprocess.check_output(args, text=True, encoding="utf-8", errors="replace").strip()

def gh(method, path, payload=None):
    cmd = ["gh", "api", "--method", method, path]
    enc = dict(encoding="utf-8", errors="replace")
    if payload is not None:
        cmd = cmd + ["--input", "-"]
        r = subprocess.run(cmd, input=json.dumps(payload), capture_output=True, text=True, **enc)
    else:
        r = subprocess.run(cmd, capture_output=True, text=True, **enc)
    if r.returncode != 0:
        raise RuntimeError("gh api failed: " + r.stderr)
    return json.loads(r.stdout)

def parse_commit(sha):
    raw = sh("git", "cat-file", "-p", sha)
    tree, parents, author, committer = None, [], None, None
    lines = raw.split("\n")
    i, msg_start = 0, None
    while i < len(lines):
        line = lines[i]
        if line.startswith("tree "): tree = line.split()[1]
        elif line.startswith("parent "): parents.append(line.split()[1])
        elif line.startswith("author "): author = line[7:]
        elif line.startswith("committer "): committer = line[10:]
        elif line == "":
            msg_start = i + 1
            break
        i += 1
    message = "\n".join(lines[msg_start:]).rstrip("\n")
    return tree, parents, author, committer, message

def parse_person(s):
    m = re.match(r"^(.*?) <(.*?)> (\d+) ([+-]\d{4})$", s)
    ts = int(m.group(3)); tz = m.group(4)
    # ISO8601 UTC
    dt = datetime.fromtimestamp(ts, tz=timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    return {"name": m.group(1), "email": m.group(2), "date": dt}

blob_cache = {}
def upload_tree(tree_sha):
    entries = sh("git", "-c", "core.quotepath=false", "ls-tree", "-r", tree_sha)
    tree_entries = []
    for line in entries.split("\n"):
        if not line: continue
        meta, path = line.split("\t", 1)
        mode, typ, sha = meta.split()
        if typ == "blob":
            if sha not in blob_cache:
                content = subprocess.check_output(["git", "cat-file", "blob", sha])
                r = gh("POST", f"repos/{REPO}/git/blobs",
                       {"content": base64.b64encode(content).decode(), "encoding": "base64"})
                blob_cache[sha] = r["sha"]
            entry_sha = blob_cache[sha]
        else:
            entry_sha = sha
        tree_entries.append({"path": path, "mode": mode, "type": typ, "sha": entry_sha})
    r = gh("POST", f"repos/{REPO}/git/trees", {"tree": tree_entries})
    return r["sha"]

def main():
    base = sh("git", "rev-parse", "origin/main")
    commits = sh("git", "rev-list", "--reverse", "origin/main..HEAD").split("\n")
    print(f"base: {base}")
    print(f"commits to push: {len(commits)}")
    parent = base
    for c in commits:
        tree, _, author, committer, message = parse_commit(c)
        new_tree = upload_tree(tree)
        payload = {
            "message": message, "tree": new_tree, "parents": [parent],
            "author": parse_person(author), "committer": parse_person(committer),
        }
        r = gh("POST", f"repos/{REPO}/git/commits", payload)
        print(f"  + {c[:8]} -> api {r['sha'][:8]} (tree {new_tree[:8]})")
        parent = r["sha"]
    # update ref
    r = gh("PATCH", f"repos/{REPO}/git/refs/heads/main", {"sha": parent, "force": True})
    print(f"ref updated -> {r['object']['sha'][:12]}")
    print("DONE")

if __name__ == "__main__":
    main()

