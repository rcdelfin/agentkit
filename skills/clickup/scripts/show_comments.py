#!/usr/bin/env python3
"""
ClickUp Task Comments — fetch and format comments for a task. The ClickUp comments
endpoint takes the task's internal UUID, so a custom ID (e.g. GYMED-793) is resolved
to its UUID first.

Usage:
    python3 show_comments.py GYMED-793            # formatted comments
    python3 show_comments.py 86exw78de            # also accepts a UUID directly
    python3 show_comments.py GYMED-793 --json     # raw JSON from the API
    python3 show_comments.py GYMED-793 --only-resolved   # resolved threads only

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
        sys.exit(1)
    except Exception as e:
        print(f"Error fetching {url}: {e}", file=sys.stderr)
        sys.exit(1)


def task_url(team_id, task_id):
    return (
        "https://api.clickup.com/api/v2/task/" + task_id
        + "?custom_task_ids=true&team_id=" + team_id
    )


CUSTOM_ID_RE = re.compile(r"^[A-Z]+-\d+$")


def is_custom_id(s):
    return bool(CUSTOM_ID_RE.match(s))


def resolve_uuid(token, team_id, task_id):
    """Return the task UUID for a custom ID (or return the input if already a UUID)."""
    if not is_custom_id(task_id):
        return task_id
    d = api_get(token, task_url(team_id, task_id))
    return d.get("id", task_id)


def fetch_comments(token, team_id, task_id):
    uuid = resolve_uuid(token, team_id, task_id)
    url = (
        "https://api.clickup.com/api/v2/task/" + uuid + "/comment"
        + "?custom_task_ids=true&team_id=" + team_id
    )
    return api_get(token, url).get("comments", [])


# ── Output ──────────────────────────────────────────────────────────────────

def fmt_ts(ms):
    if not ms:
        return "?"
    return datetime.datetime.fromtimestamp(int(ms) / 1000).strftime("%Y-%m-%d %H:%M")


def format_comment(c):
    user = c.get("user", {}).get("username", "?")
    resolved = " [RESOLVED]" if c.get("resolved") else ""
    text = c.get("comment_text", "(no text)") or "(no text)"
    attachments = [a for a in c.get("comment", []) if a.get("type") == "attachment"]

    lines = []
    lines.append(f"@ {fmt_ts(c.get('date'))} by {user}{resolved}:")
    lines.append(text)
    for a in attachments:
        # attachment block shape varies; surface filename + link if present
        name = a.get("filename") or a.get("name") or a.get("title") or "file"
        url = a.get("url") or a.get("attachment", {}).get("url") or ""
        lines.append(f"   [attachment] {name}" + (f" — {url}" if url else ""))
    return "\n".join(lines)


# ── Main ────────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(
        description="Fetch and format comments for a ClickUp task."
    )
    parser.add_argument("task_id", help="Custom ID (e.g. GYMED-793) or task UUID")
    parser.add_argument("--json", action="store_true", help="Print raw API JSON")
    parser.add_argument("--only-resolved", action="store_true",
                        help="Show only resolved comments")
    args = parser.parse_args()

    token, team_id = get_credentials()
    print(f"Fetching comments for {args.task_id}...", file=sys.stderr)

    comments = fetch_comments(token, team_id, args.task_id)
    print(f"{len(comments)} comment(s)", file=sys.stderr)

    if args.only_resolved:
        comments = [c for c in comments if c.get("resolved")]

    if args.json:
        print(json.dumps(comments, indent=2, ensure_ascii=False))
        return

    print()
    print(f"--- {len(comments)} comment(s) ---")
    for c in comments:
        print()
        print(format_comment(c))


if __name__ == "__main__":
    main()
