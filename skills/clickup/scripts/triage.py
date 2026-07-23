#!/usr/bin/env python3
"""
ClickUp Daily Task Triage — fetches open tasks, categorizes, and outputs a Markdown report.

Usage:
    python3 triage.py [--days 30] [--max-pages 15] [--mine] [--assignee USER_ID] [--output report.md]

Environment:
    Reads CLICKUP_API_TOKEN and CLICKUP_TEAM_ID from:
    1. Environment variables (preferred)
    2. ~/.hermes/.env fallback

Requires: Python 3.7+ (stdlib only — uses urllib, no pip deps)
"""

import urllib.request
import json
import time
import os
import sys
import argparse
from datetime import datetime, timedelta
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


# ── API Fetch ───────────────────────────────────────────────────────────────

USER_ID = None  # populated by --mine lookup

def fetch_tasks(token, team_id, days=30, max_pages=15, assignee=None):
    """Fetch open tasks updated within the last N days."""
    now_ms = int(time.time() * 1000)
    cutoff_ms = now_ms - (days * 24 * 60 * 60 * 1000)

    all_tasks = []
    page = 0

    while page < max_pages:
        url = (
            "https://api.clickup.com/api/v2/team/" + team_id + "/task"
            + "?include_closed=false"
            + "&date_updated_gt=" + str(cutoff_ms)
            + "&order_by=updated&reverse=true"
            + "&subtasks=true"
            + "&page=" + str(page)
        )
        if assignee:
            url += "&assignee=" + str(assignee)

        req = urllib.request.Request(url, headers={"Authorization": token})
        try:
            resp = urllib.request.urlopen(req, timeout=20)
            data = json.loads(resp.read().decode())
        except Exception as e:
            print(f"Error on page {page}: {e}", file=sys.stderr)
            break

        tasks = data.get("tasks", [])
        if not tasks:
            break

        all_tasks.extend(tasks)
        page += 1

    return all_tasks


# ── Triage Logic ────────────────────────────────────────────────────────────

def triage_tasks(tasks):
    """Categorize tasks into critical, attention, on_track."""
    now = datetime.now()
    PRIO_MAP = {"1": "urgent", "2": "high", "3": "normal", "4": "low"}
    IN_PROGRESS_STATUSES = {
        "in progress", "dev tested", "qa fail", "for prod test",
        "for review", "testing", "in qa", "deployed in production"
    }
    OPEN_STATUSES = {"to do", "open", "backlog"}

    critical = []
    attention = []
    on_track = []

    for t in tasks:
        name = t.get("name", "?")[:70]
        status = t.get("status", {}).get("status", "?")
        priority = t.get("priority")
        prio_id = str(priority.get("id", "")) if priority else "none"
        updated_ts = int(t.get("date_updated", 0))
        due_ts = t.get("due_date")
        assignees = [a.get("username", "?") for a in t.get("assignees", [])]
        list_name = t.get("list", {}).get("name", "?")
        space_name = t.get("space", {}).get("name", "?")
        task_id = t.get("id", "?")

        updated_dt = datetime.fromtimestamp(updated_ts / 1000) if updated_ts else None
        due_dt = datetime.fromtimestamp(int(due_ts) / 1000) if due_ts else None

        days_since_update = (now - updated_dt).days if updated_dt else 999
        days_until_due = (due_dt - now).days if due_dt else None

        is_urgent = prio_id == "1"
        is_high = prio_id == "2"
        is_overdue = due_dt is not None and due_dt < now
        is_due_soon = days_until_due is not None and 0 <= days_until_due <= 3
        is_in_progress = status.lower() in IN_PROGRESS_STATUSES
        is_stale = days_since_update > 7 and is_in_progress

        entry = {
            "name": name,
            "status": status,
            "priority": prio_id,
            "updated_dt": updated_dt,
            "due_dt": due_dt,
            "days_since_update": days_since_update,
            "days_until_due": days_until_due,
            "assignees": assignees,
            "list_name": list_name,
            "space_name": space_name,
            "task_id": task_id,
            "is_overdue": is_overdue,
            "is_due_soon": is_due_soon,
            "is_stale": is_stale,
            "is_urgent": is_urgent,
            "is_high": is_high,
        }

        if is_urgent or is_overdue:
            critical.append(entry)
        elif is_stale or is_due_soon or (is_high and (is_in_progress or status.lower() in OPEN_STATUSES)):
            attention.append(entry)
        else:
            on_track.append(entry)

    return critical, attention, on_track


# ── Report Generation ───────────────────────────────────────────────────────

def fmt_date(d):
    if not d:
        return "N/A"
    if isinstance(d, str):
        return d[:10]
    return d.strftime("%b %d")

def fmt_assignees(arr):
    if not arr:
        return "unassigned"
    return ", ".join(arr[:2])

PRIO_EMOJI = {"1": "🔴urgent", "2": "🟠high", "3": "normal", "4": "low"}

def generate_report(critical, attention, on_track, total_fetched, scope_label="all tasks"):
    now = datetime.now()
    lines = []
    lines.append("# 📋 Daily ClickUp Task Triage Report")
    lines.append(f"**Generated:** {now.strftime('%A, %B %d, %Y at %I:%M %p')}")
    lines.append(f"**Tasks analyzed:** {total_fetched} (open, updated in last 30 days, {scope_label})")
    lines.append("")
    lines.append("## 📊 Triage Summary")
    lines.append("")
    lines.append("| Category | Count |")
    lines.append("|----------|-------|")
    lines.append(f"| 🔴 Critical (urgent / overdue) | **{len(critical)}** |")
    lines.append(f"| 🟡 Needs Attention (stale / due soon / high priority) | **{len(attention)}** |")
    lines.append(f"| 🟢 On Track | **{len(on_track)}** |")
    lines.append("")

    # ── Critical ──
    overdue = [t for t in critical if t["is_overdue"]]
    urgent = [t for t in critical if not t["is_overdue"] and t["is_urgent"]]
    overdue.sort(key=lambda x: x.get("days_until_due", 0))
    urgent.sort(key=lambda x: x.get("days_since_update", 0), reverse=True)

    lines.append("---")
    lines.append("## 🔴 Critical — Action Required")
    lines.append("")

    if overdue:
        lines.append(f"### ⏰ Overdue ({len(overdue)} tasks)")
        lines.append("")
        for t in overdue[:15]:
            d = abs(t.get("days_until_due", 0)) or "?"
            prio = PRIO_EMOJI.get(t.get("priority", ""), "")
            lines.append(f"- **{t['name']}**")
            lines.append(f"  - `{t['status']}` | {prio} | Due: {fmt_date(t.get('due_dt'))} ({d}d overdue) | {fmt_assignees(t.get('assignees'))}")
        if len(overdue) > 15:
            lines.append(f"- _...and {len(overdue) - 15} more overdue tasks_")
        lines.append("")

    if urgent:
        lines.append(f"### 🚨 Urgent Priority ({len(urgent)} tasks)")
        lines.append("")
        for t in urgent[:10]:
            lines.append(f"- **{t['name']}**")
            lines.append(f"  - `{t['status']}` | Due: {fmt_date(t.get('due_dt'))} | {fmt_assignees(t.get('assignees'))}")
        if len(urgent) > 10:
            lines.append(f"- _...and {len(urgent) - 10} more urgent tasks_")
        lines.append("")

    # ── Needs Attention ──
    stale = [t for t in attention if t["is_stale"]]
    due_soon = [t for t in attention if t.get("is_due_soon") and not t.get("is_stale")]
    high_active = [t for t in attention if t.get("is_high") and not t.get("is_stale") and not t.get("is_due_soon")]
    stale.sort(key=lambda x: x.get("days_since_update", 0), reverse=True)
    due_soon.sort(key=lambda x: x.get("days_until_due", 999))

    lines.append("---")
    lines.append("## 🟡 Needs Attention")
    lines.append("")

    if stale:
        lines.append(f"### 💤 Stale In-Progress ({len(stale)} tasks — no update in 7+ days)")
        lines.append("")
        for t in stale[:10]:
            lines.append(f"- **{t['name']}** — {t.get('days_since_update', '?')}d stale")
            lines.append(f"  - `{t['status']}` | {t.get('list_name', '?')} | {fmt_assignees(t.get('assignees'))}")
        if len(stale) > 10:
            lines.append(f"- _...and {len(stale) - 10} more stale tasks_")
        lines.append("")

    if due_soon:
        lines.append(f"### 📅 Due Soon ({len(due_soon)} tasks — due within 3 days)")
        lines.append("")
        for t in due_soon[:10]:
            lines.append(f"- **{t['name']}** — due in {t.get('days_until_due', '?')}d")
            lines.append(f"  - `{t['status']}` | Due: {fmt_date(t.get('due_dt'))} | {fmt_assignees(t.get('assignees'))}")
        if len(due_soon) > 10:
            lines.append(f"- _...and {len(due_soon) - 10} more_")
        lines.append("")

    if high_active:
        lines.append(f"### 🟠 High Priority Active ({len(high_active)} tasks)")
        lines.append("")
        for t in high_active[:8]:
            lines.append(f"- **{t['name']}**")
            lines.append(f"  - `{t['status']}` | {t.get('list_name', '?')} | {fmt_assignees(t.get('assignees'))}")
        if len(high_active) > 8:
            lines.append(f"- _...and {len(high_active) - 8} more_")
        lines.append("")

    # ── On Track ──
    lines.append("---")
    lines.append("## 🟢 On Track")
    lines.append(f"**{len(on_track)} tasks** proceeding normally with recent updates and no immediate concerns.")
    lines.append("")

    # ── Recommendations ──
    lines.append("---")
    lines.append("## 🎯 What to Work on First")
    lines.append("")
    n = 1
    for t in overdue[:3]:
        d = abs(t.get("days_until_due", 0)) or "?"
        lines.append(f"{n}. **{t['name']}** — {d}d overdue, `{t['status']}`. Check blockers or reassign. ({fmt_assignees(t.get('assignees'))})")
        n += 1
    for t in urgent[:2]:
        lines.append(f"{n}. **{t['name']}** — Urgent, `{t['status']}`. Due: {fmt_date(t.get('due_dt'))}. ({fmt_assignees(t.get('assignees'))})")
        n += 1
    for t in stale[:3]:
        lines.append(f"{n}. **{t['name']}** — {t.get('days_since_update', '?')}d stale. Needs status update or unblocking.")
        n += 1
    lines.append("")
    lines.append("---")
    lines.append("*Generated by Hermes ClickUp Triage*")

    return "\n".join(lines)


# ── Main ────────────────────────────────────────────────────────────────────

def lookup_own_user_id(token):
    """Fetch current user's ClickUp user ID from /api/v2/user."""
    try:
        req = urllib.request.Request(
            "https://api.clickup.com/api/v2/user",
            headers={"Authorization": token}
        )
        resp = urllib.request.urlopen(req, timeout=10)
        data = json.loads(resp.read().decode())
        return data.get("user", {}).get("id")
    except Exception as e:
        print(f"Warning: Could not look up user ID: {e}", file=sys.stderr)
        return None


def main():
    parser = argparse.ArgumentParser(description="ClickUp Daily Task Triage")
    parser.add_argument("--days", type=int, default=30, help="Lookback window in days")
    parser.add_argument("--max-pages", type=int, default=15, help="Max API pages to fetch")
    parser.add_argument("--output", type=str, default=None, help="Output file (default: stdout)")
    parser.add_argument("--mine", action="store_true", help="Only show tasks assigned to me")
    parser.add_argument("--assignee", type=str, default=None, help="Filter by ClickUp user ID")
    args = parser.parse_args()

    token, team_id = get_credentials()

    # Resolve --mine to user ID
    assignee = args.assignee
    scope_label = "all assignees"
    if args.mine:
        uid = lookup_own_user_id(token)
        if uid:
            assignee = str(uid)
            scope_label = "assigned to me"
            print(f"Filtering by my user ID: {uid}", file=sys.stderr)
        else:
            print("WARNING: --mine requested but couldn't determine user ID. Showing all tasks.", file=sys.stderr)
    elif assignee:
        scope_label = f"user ID {assignee}"

    print(f"Fetching tasks (team {team_id}, last {args.days} days)...", file=sys.stderr)

    tasks = fetch_tasks(token, team_id, days=args.days, max_pages=args.max_pages, assignee=assignee)
    print(f"Fetched {len(tasks)} open tasks", file=sys.stderr)

    # Client-side filter: only keep tasks where user is in the assignees list
    if assignee:
        assignee_int = int(assignee)
        before = len(tasks)
        tasks = [t for t in tasks if assignee_int in [a.get("id") for a in t.get("assignees", [])]]
        print(f"Filtered to {len(tasks)} tasks directly assigned to user (removed {before - len(tasks)})", file=sys.stderr)
    print(f"Fetched {len(tasks)} open tasks", file=sys.stderr)

    critical, attention, on_track = triage_tasks(tasks)
    report = generate_report(critical, attention, on_track, len(tasks), scope_label=scope_label)

    if args.output:
        Path(args.output).write_text(report)
        print(f"Report written to {args.output}", file=sys.stderr)
    else:
        print(report)


if __name__ == "__main__":
    main()
