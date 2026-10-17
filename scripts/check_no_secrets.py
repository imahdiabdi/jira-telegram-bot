#!/usr/bin/env python3
"""Fail if any private value from a local config.private.json appears in a tracked file.

Usage:  python3 scripts/check_no_secrets.py [config.private.json]
config.private.json is git-ignored: it lists YOUR real values (host, ids, names, handles).
It also flags anything that looks like a Telegram ID, a JIRAUSER key or an API token.
"""
import json, os, re, subprocess, sys

GENERIC = {"admin", "member", "lead", "guest", "task", "subtask", "bug", "true", "false", "null"}
cfg_path = sys.argv[1] if len(sys.argv) > 1 else "config.private.json"
terms = set()
if os.path.exists(cfg_path):
    def walk(o):
        if isinstance(o, dict):
            for v in o.values(): walk(v)
        elif isinstance(o, list):
            for v in o: walk(v)
        elif isinstance(o, str) and len(o) >= 4 and o.lower() not in GENERIC \
                and not (o.isdigit() and len(o) < 7):
            terms.add(o)
    walk(json.load(open(cfg_path, encoding="utf-8")))
else:
    print(f"note: {cfg_path} not found, running pattern checks only")

patterns = [r"\bJIRAUSER(?!1000[1-5]\b)[0-9]{5,}\b", r"(?<![0-9])[0-9]{9,10}(?![0-9])", r"AIza[\w-]{30,}", r"\b\d{8,10}:[\w-]{30,}\b", r"Bearer\s+[A-Za-z0-9._-]{20,}"]
files = subprocess.run(["git", "ls-files"], capture_output=True, text=True).stdout.split() or \
        [os.path.join(r, f) for r, _, fs in os.walk(".") if ".git" not in r for f in fs]
bad = 0
for f in files:
    if f.endswith((".png", ".mp4", ".gif")) or f.endswith("check_no_secrets.py"):
        continue
    try: text = open(f, encoding="utf-8").read()
    except Exception: continue
    low = text.lower()
    for t in terms:
        if t.lower() in low:
            print(f"LEAK  {f}: contains private value {t!r}"); bad += 1
    for p in patterns:
        for m in re.finditer(p, text):
            print(f"SUSPECT  {f}: {m.group(0)[:40]!r}"); bad += 1
print("OK: nothing private found" if not bad else f"FAILED: {bad} problem(s). Do not publish.")
sys.exit(1 if bad else 0)
