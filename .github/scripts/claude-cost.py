#!/usr/bin/env python3
"""Approximate cost of @claude runs, shown where the owner reads.

  claude-cost.py record <execution-file> <issue-or-pr> <run-id>
      append the run's cost to Claude's progress comment for that run, then
      refresh the total on the PR(s) it belongs to
  claude-cost.py total <issue-or-pr>
      refresh the total: on that PR, or on the open PRs Claude made from that
      issue (branches claude/issue-<N>-...)

The cost is Claude Code's own estimate at API list prices (total_cost_usd), so
it is approximate. Each run's cost is kept in a hidden marker in its comment;
a PR's total adds up the markers on the PR and on the issue it came from.
Needs gh with GH_TOKEN and GITHUB_REPOSITORY.
"""
import json
import os
import re
import subprocess
import sys

REPO = os.environ.get("GITHUB_REPOSITORY", "")
MARK = re.compile(r"<!-- claude-cost: ([0-9.]+) run:(\d+) -->")
TOTAL_MARK = "<!-- claude-cost-total -->"
BRANCH = re.compile(r"^claude/issue-(\d+)-")


def gh(*args, data=None):
    out = subprocess.run(["gh", "api", *args] + (["--input", "-"] if data is not None else []),
                         input=json.dumps(data) if data is not None else None,
                         capture_output=True, text=True, check=True).stdout
    return out


def comments(number):
    out = gh("--paginate", f"repos/{REPO}/issues/{number}/comments", "--jq", ".[] | @json")
    return [json.loads(line) for line in out.splitlines() if line]


def czk(usd):  # Czech formatting of the dollar amount: 1,51 USD
    return f"{usd:.2f}".replace(".", ",") + " USD"


def run_cost(path):
    try:
        with open(path) as f:
            text = f.read()
    except OSError:
        return None
    try:
        messages = json.loads(text)
    except ValueError:  # JSON lines
        messages = [json.loads(line) for line in text.splitlines() if line.strip()]
    if isinstance(messages, dict):
        messages = [messages]
    costs = [m["total_cost_usd"] for m in messages
             if isinstance(m, dict) and m.get("type") == "result" and "total_cost_usd" in m]
    return costs[-1] if costs else None


def record(path, number, run_id):
    cost = run_cost(path)
    if cost is None:
        print("no cost in execution file, nothing to record")
        return
    line = f"\n\n<sub>💰 Přibližná cena tohoto běhu: {czk(cost)}</sub>\n<!-- claude-cost: {cost:.4f} run:{run_id} -->"
    run_link = f"/actions/runs/{run_id}"
    mine = [c for c in comments(number) if run_link in c["body"]]
    try:
        c = mine[-1]
        body = re.sub(r"\n\n<sub>(?:💰 )?Přibližná cena tohoto běhu:[^\n]*</sub>\n" + MARK.pattern, "", c["body"])
        gh("-X", "PATCH", f"repos/{REPO}/issues/comments/{c['id']}", data={"body": body + line})
    except (IndexError, subprocess.CalledProcessError) as e:
        # progress comment not found or not editable: say it in a comment of its own
        print(f"progress comment not updated ({e}), posting a separate one")
        gh("-X", "POST", f"repos/{REPO}/issues/{number}/comments", data={"body": line.strip()})
    print(f"run {run_id}: {cost:.4f} USD")
    total(number)


def costs_in(number):
    return {run: float(usd) for c in comments(number) for usd, run in MARK.findall(c["body"])}


def total_for_pr(pr):
    runs = costs_in(pr["number"])
    m = BRANCH.match(pr["head"]["ref"])
    if m:
        runs.update(costs_in(int(m.group(1))))
    if not runs:
        return
    usd = sum(runs.values())
    body = (f"{TOTAL_MARK}\n### 💰 Cena práce Clauda\n\n"
            f"Tenhle návrh změny zatím stál přibližně **{czk(usd)}** "
            f"({len(runs)} {'běh' if len(runs) == 1 else 'běhy' if len(runs) < 5 else 'běhů'} Clauda"
            + (f", včetně zadání v issue #{m.group(1)}" if m else "") + ").\n\n"
            "<sub>Odhad podle ceníku Anthropic API; přesnou částku ukazuje vyúčtování.</sub>")
    existing = [c for c in comments(pr["number"]) if TOTAL_MARK in c["body"]]
    if existing:
        if existing[-1]["body"] != body:
            gh("-X", "PATCH", f"repos/{REPO}/issues/comments/{existing[-1]['id']}", data={"body": body})
    else:
        gh("-X", "POST", f"repos/{REPO}/issues/{pr['number']}/comments", data={"body": body})
    print(f"PR #{pr['number']}: {usd:.4f} USD over {len(runs)} runs")


def total(number):
    issue = json.loads(gh(f"repos/{REPO}/issues/{number}"))
    if "pull_request" in issue:
        prs = [json.loads(gh(f"repos/{REPO}/pulls/{number}"))]
    else:
        out = gh("--paginate", f"repos/{REPO}/pulls?state=open", "--jq", ".[] | @json")
        prs = [p for p in map(json.loads, filter(None, out.splitlines()))
               if (m := BRANCH.match(p["head"]["ref"])) and int(m.group(1)) == number]
    for pr in prs:
        total_for_pr(pr)


if __name__ == "__main__":
    cmd, *args = sys.argv[1:] or [""]
    if cmd == "record" and len(args) == 3:
        record(args[0], int(args[1]), args[2])
    elif cmd == "total" and len(args) == 1:
        total(int(args[0]))
    else:
        sys.exit(__doc__)
