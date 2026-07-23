#!/usr/bin/env python3
"""
ClickUp Task Card Pull — fetch a single task by custom ID (or UUID) and print a
formatted summary. Replaces the inline `curl | python3 -c "..."` one-liner.

Usage:
    python3 show_task.py GYMED-793            # full formatted card (default)
    python3 show_task.py GYMED-793 --meta     # header / status / assignee only
    python3 show_task.py GYMED-793 --json     # raw JSON from the API

Environment:
    Reads CLICKUP_API_TOKEN and CLICKUP_TEAM_ID from:
    1. Environment variables (preferred)
    2. ~/.hermes/.env fallback

Requires: Python 3.7+ (stdlib only — uses urllib, no pip deps)
"""

import urllib.request
import urllib.error
import argparse
import datetime
import json
import sys
import os
import re
from pathlib import Path


# ── Config ──────────────────────────────────────────────────────────────────

def get_credentials():
    """Get ClickUp API token and team ID from env or ~/.hermes/.env."""
    token = os.environ.get("CLICKUP_API_TOKEN", "")
    team_id = os.environ.get("CLICKUP_TEAM_ID", "")

    if token and team_id:
        return token, team_id

    # Fallback: read from ~/.hermes/.env
    env_file = Path.home() / ".hermes" / ".env"
    if env_file.exists():
        for line in env_file.read_text().splitlines():
            line = line.strip()
            if line.startswith("#") or "=" not in line:
                continue
            key, _, value = line.partition("=")
            key = key.strip()
            value = value.strip().strip('"').strip("'")
            if key == "CLICKUP_API_TOKEN" and not token:
                token = value
            elif key == "CLICKUP_TEAM_ID" and not team_id:
                team_id = value

    if not token:
        print("ERROR: CLICKUP_API_TOKEN not found in env or ~/.hermes/.env", file=sys.stderr)
        sys.exit(1)
    if not team_id:
        print("ERROR: CLICKUP_TEAM_ID not found in env or ~/.hermes/.env", file=sys.stderr)
        sys.exit(1)

    return token, team_id


# ── API ─────────────────────────────────────────────────────────────────────

def api_get(token, url):
    req = urllib.request.Request(url, headers={"Authorization": token})
    try:
        resp = urllib.request.urlopen(req, timeout=20)
        return json.loads(resp.read().decode())
    except urllib.error.HTTPError as e:
        body = e.read().decode()
        print(f"HTTP {e.code}: {body}", file=sys.stderr)
        if e.code == 401:
            print("Hint: personal tokens use no 'Bearer' prefix — just pk_xxxxx.", file=sys.stderr)
        if "OAUTH_027" in body or "Team not authorized" in body:
            print("Hint: custom IDs need uppercase-hyphen form (GYMED-793, not gymed793) "
                  "and a valid CLICKUP_TEAM_ID.", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"Error fetching {url}: {e}", file=sys.stderr)
        sys.exit(1)


def task_url(team_id, task_id):
    # custom_task_ids=true is harmless for UUID lookups too
    return (
        "https://api.clickup.com/api/v2/task/" + task_id
        + "?custom_task_ids=true&team_id=" + team_id
    )


def fetch_task(token, team_id, task_id):
    return api_get(token, task_url(team_id, task_id))


def resolve_parent(token, team_id, parent_uuid):
    """Return (custom_id, name, status) for a parent UUID, or None on failure."""
    try:
        d = api_get(token, task_url(team_id, parent_uuid))
        return (
            d.get("custom_id") or "?",
            d.get("name", "?"),
            d.get("status", {}).get("status", "?"),
        )
    except SystemExit:
        return None


# ── Formatting helpers ──────────────────────────────────────────────────────

def fmt_ts(ms):
    if not ms:
        return "-"
    return datetime.datetime.fromtimestamp(int(ms) / 1000).strftime("%Y-%m-%d %H:%M")


def fmt_cf_value(v):
    """Render a custom field value readably."""
    if v is None:
        return ""
    if isinstance(v, dict):
        if "name" in v:
            return str(v["name"])
        if "percent_complete" in v:
            return f"{v['percent_complete']}%"
        return json.dumps(v, ensure_ascii=False)
    if isinstance(v, list):
        items = []
        for el in v:
            if isinstance(el, dict):
                items.append(str(el.get("name") or el.get("id") or el))
            else:
                items.append(str(el))
        return ", ".join(items)
    return str(v)


CUSTOM_ID_RE = re.compile(r"^[A-Z]+-\d+$")


def is_custom_id(s):
    return bool(CUSTOM_ID_RE.match(s))


# ── Output ──────────────────────────────────────────────────────────────────

def print_meta(d):
    assignees = ", ".join(a.get("username", "?") for a in d.get("assignees", [])) or "unassigned"
    status = d.get("status", {}).get("status", "?")
    print(f'{d.get("custom_id", "")} | {d.get("name", "?")}')
    print(f"Status: {status} | Assignees: {assignees}")


def print_full(d, token, team_id):
    name = d.get("name", "?")
    status = d.get("status", {}).get("status", "?")
    priority = d.get("priority") or {}
    prio_str = priority.get("priority", "none")
    assignees = ", ".join(a.get("username", "?") for a in d.get("assignees", [])) or "unassigned"
    parent = d.get("parent")

    bar = "=" * 60
    print(bar)
    print(name)
    print(bar)
    print(f"Status: {status}  |  Priority: {prio_str}  |  Assignee(s): {assignees}")
    print(f'Custom ID: {d.get("custom_id", "?")}  |  UUID: {d.get("id", "?")}')

    if parent and parent != "none":
        resolved = resolve_parent(token, team_id, parent)
        if resolved:
            cid, pname, pstatus = resolved
            print(f"Parent: {cid} {pname} ({pstatus})")
        else:
            print(f"Parent UUID: {parent}")

    print(f'Created: {fmt_ts(d.get("date_created"))}')
    print(f'Updated: {fmt_ts(d.get("date_updated"))}')
    if d.get("due_date"):
        print(f'Due: {fmt_ts(d.get("due_date"))}')

    tags = [t["name"] for t in d.get("tags", [])]
    if tags:
        print(f"Tags: {', '.join(tags)}")

    if d.get("list"):
        print(f'List: {d["list"].get("name", "?")}')
    if d.get("folder"):
        print(f'Folder: {d["folder"].get("name", "?")}')
    if d.get("space"):
        print(f'Space: {d["space"].get("name", "?")}')

    print()

    deps = d.get("dependencies", [])
    if deps:
        print("--- Dependencies ---")
        for dep in deps:
            conf = dep.get("config", {})
            print(f'  - {dep.get("type", "?")} - config: {json.dumps(conf)}')

    linked = d.get("linked_tasks", [])
    if linked:
        print("--- Linked Tasks ---")
        for lt in linked:
            print(f'  - {lt.get("custom_id", "")}: {lt.get("name", "")} ({lt.get("id", "")})')

    cfs = d.get("custom_fields", [])
    if cfs:
        print("--- Custom Fields ---")
        for cf in cfs:
            val = fmt_cf_value(cf.get("value", cf.get("parsed_value")))
            print(f'  - {cf.get("name", "?")}: {val}')

    subtasks = d.get("subtasks", [])
    if subtasks:
        print()
        print("--- Subtasks ---")
        for st in subtasks:
            sstatus = st.get("status", {}).get("status", "?") if isinstance(st.get("status"), dict) else st.get("status", "?")
            print(f'  - {st.get("custom_id", "")}: {st.get("name", "")} ({sstatus})')

    print()
    tc = d.get("text_content", "")
    if tc:
        print("--- Description ---")
        print(tc)

    print()
    print(f'URL: {d.get("url", "")}')


# ── Main ────────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(
        description="Fetch and format a single ClickUp task by custom ID or UUID."
    )
    parser.add_argument("task_id", help="Custom ID (e.g. GYMED-793) or task UUID")
    parser.add_argument("--meta", action="store_true", help="Print header/status/assignee only")
    parser.add_argument("--json", action="store_true", help="Print raw API JSON")
    args = parser.parse_args()

    token, team_id = get_credentials()

    if is_custom_id(args.task_id):
        print(f'Fetching {args.task_id} (custom ID)...', file=sys.stderr)
    else:
        print(f'Fetching task {args.task_id} (UUID)...', file=sys.stderr)

    d = fetch_task(token, team_id, args.task_id)

    if args.json:
        print(json.dumps(d, indent=2, ensure_ascii=False))
    elif args.meta:
        print_meta(d)
    else:
        print_full(d, token, team_id)


if __name__ == "__main__":
    main()
